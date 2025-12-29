# dashboard/app_v2.py
"""
Streamlit dashboard (SolarWinds-like) for visualizing flow traffic as stacked area,
top conversations, and quick stats. Uses capture CSVs or preprocessed flow CSVs.
Run:
    streamlit run dashboard/app_v2.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import glob, os, math
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="CovertChannel — Traffic Dashboard")

st.title("Covert Timing Channel — Traffic Summary (SolarWinds style)")

# ------------------------
# Helpers
# ------------------------
def load_capture_csvs(capture_glob="capture/*.csv"):
    files = sorted(glob.glob(capture_glob))
    if not files:
        return None, []
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df['source_file'] = os.path.basename(f)
            dfs.append(df)
        except Exception:
            continue
    if not dfs:
        return None, files
    df = pd.concat(dfs, ignore_index=True)
    # ensure types
    if 'ts' in df.columns:
        df['ts'] = df['ts'].astype(float)
    if 'length' in df.columns:
        df['length'] = df['length'].astype(float)
    return df, files

def flows_from_preprocessed(flow_glob="preprocessed/flows/*.csv"):
    files = sorted(glob.glob(flow_glob))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            # ensure ts and length exist; if not, keep index as pseudo-ts
            if 'ts' not in df.columns:
                # create synthetic ts from ipd
                if 'ipd' in df.columns:
                    df['ts'] = df['ipd'].cumsum()
                else:
                    df['ts'] = np.arange(len(df)) * 0.001
            if 'length' not in df.columns:
                df['length'] = df.get('pkt_len', df.get('len', 64))
            df['flow'] = os.path.basename(f).replace('.csv','')
            dfs.append(df[['ts','flow','length','src','dst']])
        except Exception:
            continue
    if not dfs:
        return None, files
    return pd.concat(dfs, ignore_index=True), files

def prepare_time_series(df, time_col='ts', length_col='length', flow_col='flow',
                        bin_s=1.0, start=None, end=None):
    """Aggregate bytes per flow into time bins of bin_s seconds."""
    # build time index (in seconds relative)
    if start is None:
        start = df[time_col].min()
    if end is None:
        end = df[time_col].max()
    # create bins
    n_bins = max(1, math.ceil((end - start) / bin_s))
    bins = np.linspace(start, start + n_bins*bin_s, n_bins+1)
    labels = [start + i*bin_s for i in range(n_bins)]
    df['time_bin'] = pd.cut(df[time_col], bins=bins, labels=labels, include_lowest=True)
    # sum bytes per bin-flow
    agg = df.groupby(['time_bin', flow_col])[length_col].sum().reset_index()
    # pivot to wide form
    pivot = agg.pivot(index='time_bin', columns=flow_col, values=length_col).fillna(0)
    # convert index to datetime for plotting convenience
    pivot = pivot.reset_index()
    pivot['time_dt'] = pd.to_datetime(pivot['time_bin'].astype(float), unit='s')
    return pivot.sort_values('time_dt').reset_index(drop=True)

def top_n_summary(df, flow_col='flow', length_col='length', n=5):
    s = df.groupby(flow_col)[length_col].sum().sort_values(ascending=False)
    top = s.head(n).reset_index().rename(columns={length_col:'bytes'})
    total = s.sum()
    top['percent'] = (top['bytes'] / total * 100).round(2)
    return top, total

# ------------------------
# Load data
# ------------------------
st.sidebar.header("Data source")
use_capture = st.sidebar.radio("Load data from", ("capture CSVs", "preprocessed flows (recommended)"))

if use_capture == "capture CSVs":
    df_capture, cap_files = load_capture_csvs()
    if df_capture is None:
        st.sidebar.error("No capture CSVs found in capture/*.csv")
        st.stop()
    st.sidebar.write(f"Found {len(cap_files)} capture file(s)")
    df_data = df_capture.copy()
    # create a 'flow' column if not present
    if 'flow' not in df_data.columns:
        df_data['flow'] = df_data.apply(lambda r: f"{r.get('src','?')}_{r.get('dst','?')}_{r.get('proto','?')}", axis=1)
else:
    df_data, flow_files = flows_from_preprocessed()
    if df_data is None:
        st.sidebar.error("No preprocessed flows found in preprocessed/flows/*.csv")
        st.stop()
    st.sidebar.write(f"Found {len(flow_files)} flow file(s)")

# time range controls
min_ts = float(df_data['ts'].min())
max_ts = float(df_data['ts'].max())
duration = max_ts - min_ts
st.sidebar.markdown(f"**Time span:**** {duration:.2f} s**")
bin_s = st.sidebar.slider("Bin size (seconds)", min_value=0.01, max_value=5.0, value=0.5, step=0.01)
start_offset = st.sidebar.slider("Start offset (seconds from start)", 0.0, float(duration), 0.0, step=0.1)
end_offset = st.sidebar.slider("End offset (seconds from start)", 0.0, float(duration), float(duration), step=0.1)
start = min_ts + start_offset
end = min_ts + end_offset
top_n = st.sidebar.slider("Top N flows to show (stacked)", 1, 12, 6)

# filter data by time window
df_window = df_data[(df_data['ts'] >= start) & (df_data['ts'] <= end)].copy()
if df_window.empty:
    st.error("No packets in selected time window. Adjust sliders.")
    st.stop()

# compute summary & aggregated time series
pivot = prepare_time_series(df_window, bin_s=bin_s, flow_col='flow')
# compute total bytes per flow in the window
flow_sums = df_window.groupby('flow')['length'].sum().sort_values(ascending=False)
top_flows = list(flow_sums.head(top_n).index)

# fill other flows into "Other"
all_flow_cols = [c for c in pivot.columns if c not in ('time_bin','time_dt')]
# ensure the top flows exist in pivot (if some flows absent, they'll be ignored)
stack_cols = [c for c in all_flow_cols if c in top_flows]
other_cols = [c for c in all_flow_cols if c not in stack_cols]
if other_cols:
    pivot['Other'] = pivot[other_cols].sum(axis=1)
    stack_cols = stack_cols + (['Other'] if 'Other' not in stack_cols else [])

# ------------------------
# Layout: main large area + scrubber + right summary
# ------------------------
col1, col2 = st.columns([3,1])

with col1:
    st.subheader("Traffic over time — stacked area (bytes per bin)")
    # prepare melt for px.area
    df_plot = pivot[['time_dt'] + stack_cols].melt(id_vars='time_dt', var_name='flow', value_name='bytes')
    # colors: pick a nice palette; we encourage fewer colors to match SolarWinds style
    fig = px.area(df_plot, x='time_dt', y='bytes', color='flow',
                  labels={'time_dt':'Time','bytes':'Bytes'},
                  title=None)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
                      margin=dict(l=10,r=10,t=10,b=10), showlegend=True)
    # Y-axis display in kbps-like: convert bytes per bin to kbps if desired
    st.plotly_chart(fig, use_container_width=True, height=420)

    # scrubber / mini chart (sparkline)
    st.subheader("Mini timeline (scrubber)")
    mini = pivot.copy()
    mini['total'] = mini[all_flow_cols].sum(axis=1) if all_flow_cols else mini[stack_cols].sum(axis=1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=mini['time_dt'], y=mini['total'], mode='lines', fill='tozeroy', name='total'))
    fig2.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=140, showlegend=False, xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Top Conversations")
    top_table, total_bytes = top_n_summary(df_window, flow_col='flow', length_col='length', n=top_n)
    # display stacked bar for top N
    # build bar: each flow's total bytes
    bar_fig = px.bar(top_table, x='flow', y='bytes', text='percent', labels={'bytes':'Bytes','flow':'Flow'})
    bar_fig.update_layout(margin=dict(l=5,r=5,t=10,b=10), height=220, showlegend=False)
    st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("**Top conversations (table)**")
    st.dataframe(top_table.rename(columns={'flow':'Conversation','bytes':'Bytes','percent':'Share (%)'}).head(10), height=240)

    st.markdown("**Quick stats**")
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total flows", int(df_window['flow'].nunique()))
        st.metric("Total bytes", f"{int(df_window['length'].sum()):,}")
    with colB:
        st.metric("Time span (s)", f"{(end-start):.2f}")
        st.metric("Bin size (s)", f"{bin_s:.2f}")

# bottom: small table of top endpoints (src or dst summary)
st.markdown("---")
st.subheader("Top endpoints (source IP)")
src_summary = df_window.groupby('src')['length'].sum().sort_values(ascending=False).reset_index().rename(columns={'length':'bytes'})
st.table(src_summary.head(8))

st.markdown("""
**Tips:**  
- Use the left-side sliders to zoom the time window and change bin size.  
- Try preprocessed flows for clearer conversation grouping (recommended).
""")
