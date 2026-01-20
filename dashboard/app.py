import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Covert Timing Channel IDS",
    layout="wide",
)

ALERT_LOG = "live/alerts.csv"

# ---------------- STYLES ----------------
st.markdown("""
<style>
body { background-color: #0e1117; }
.metric-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #161b22;
    text-align: center;
}
.badge-high { color:#ff4b4b; font-weight:bold; }
.badge-medium { color:#facc15; font-weight:bold; }
.badge-low { color:#22c55e; font-weight:bold; }
.badge-proto { padding:3px 6px; border-radius:6px; background:#222; }
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def load_alerts(path):
    if not st.session_state.get("alerts_cache"):
        try:
            df = pd.read_csv(
                path,
                on_bad_lines="skip",
                engine="python"
            )
            st.session_state.alerts_cache = df
        except:
            return pd.DataFrame()
    return st.session_state.alerts_cache.copy()

def severity_label(risk):
    if risk >= 70:
        return "High"
    elif risk >= 50:
        return "Medium"
    else:
        return "Low"

def sev_badge(sev):
    cls = {
        "High":"badge-high",
        "Medium":"badge-medium",
        "Low":"badge-low"
    }.get(sev,"")
    return f"<span class='{cls}'>● {sev}</span>"

def proto_badge(p):
    return f"<span class='badge-proto'>{p}</span>"

# ---------------- LOAD DATA ----------------
alerts = load_alerts(ALERT_LOG)
if alerts.empty:
    st.warning("No alerts available yet. Start realtime detector.")
    st.stop()

alerts["time"] = alerts["timestamp"].apply(
    lambda x: datetime.fromtimestamp(x).strftime("%H:%M:%S")
)
alerts["Severity"] = alerts["final_risk"].apply(severity_label)
alerts["protocol"] = alerts["flow"].apply(lambda x: x.split("_")[-1])

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

protocols = sorted(alerts["protocol"].unique())
proto_filter = st.sidebar.multiselect(
    "Protocol",
    protocols,
    default=protocols
)

risk_range = st.sidebar.slider(
    "Risk Range",
    0, 100, (60, 100)
)

# ---------------- FILTER ----------------
filtered = alerts[
    (alerts["protocol"].isin(proto_filter)) &
    (alerts["final_risk"].between(*risk_range))
]

# ---------------- HEADER ----------------
st.markdown("## 🛡️ Covert Timing Channel IDS — Real-Time SOC Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Alerts", len(filtered))
with col2:
    st.metric("High Risk", (filtered["Severity"]=="High").sum())
with col3:
    st.metric("Medium Risk", (filtered["Severity"]=="Medium").sum())
with col4:
    st.metric("Low Risk", (filtered["Severity"]=="Low").sum())

st.markdown("---")

# ---------------- TIMELINE REPLAY ----------------
st.markdown("### ⏱️ Attack Timeline Replay")

min_t = filtered["timestamp"].min()
max_t = filtered["timestamp"].max()

replay_t = st.slider(
    "Replay alerts up to time",
    min_value=float(min_t),
    max_value=float(max_t),
    value=float(max_t),
    step=1.0
)

timeline = filtered[filtered["timestamp"] <= replay_t]

fig = px.line(
    timeline,
    x="time",
    y="final_risk",
    title="Risk Trend Over Time",
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# ---------------- LIVE ALERTS ----------------
st.markdown("### 🚨 Live Alerts")

rows_to_show = st.selectbox(
    "Show latest alerts",
    [5, 10, 15, 25, 50, 100],
    index=2
)

latest = (
    timeline
    .sort_values("timestamp", ascending=False)
    .head(rows_to_show)
)

latest["Severity"] = latest["Severity"].apply(sev_badge)
latest["protocol"] = latest["protocol"].apply(proto_badge)

st.write(
    latest[[
        "time","flow","protocol","final_risk",
        "Severity","ml_prob","stat_score","iforest_risk"
    ]].to_html(escape=False, index=False),
    unsafe_allow_html=True
)

# ---------------- TOP FLOWS ----------------
st.markdown("### 🔥 Top Suspicious Flows")

top_flows = (
    timeline.groupby("flow")["final_risk"]
    .mean()
    .reset_index()
    .sort_values("final_risk", ascending=False)
    .head(5)
)

st.dataframe(top_flows)

# ---------------- FOOTER ----------------
st.markdown("""
---
**Legend**
- 🔴 High → Likely covert timing channel  
- 🟡 Medium → Suspicious timing anomaly  
- 🟢 Low → Normal traffic  

*Auto-blocking supported on Linux (iptables) / Windows Defender (PowerShell)*  
*Academic & Research Use*
""")
