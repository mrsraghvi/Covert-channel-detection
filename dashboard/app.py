"""
Covert Channel IDS — Real-Time Dashboard
---------------------------------------
Features:
- Severity coloring (Green / Yellow / Red)
- Protocol filtering (TCP / UDP / ICMP / HTTP / HTTPS / SSL)
- Timeline replay (attack reconstruction)
- Robust CSV parsing (no crashes)
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Covert Channel IDS",
    layout="wide"
)

ALERT_LOG = "live/alerts.csv"

# ---------------- HELPERS ----------------
def load_alerts(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(
            path,
            engine="python",
            on_bad_lines="skip"
        )

    expected_cols = [
        "timestamp",
        "flow",
        "protocol",
        "final_risk",
        "ml_prob",
        "stat_score",
        "iforest_risk"
    ]

    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    df = df[expected_cols]
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["time"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x).strftime("%H:%M:%S")
        if pd.notnull(x) else "NA"
    )

    df["final_risk"] = pd.to_numeric(df["final_risk"], errors="coerce")
    return df.dropna(subset=["final_risk"])

def severity_color(risk):
    if risk >= 70:
        return "🔴 High"
    elif risk >= 50:
        return "🟡 Medium"
    else:
        return "🟢 Low"

# ---------------- LOAD DATA ----------------
alerts = load_alerts(ALERT_LOG)

st.title("🛡️ Covert Timing Channel IDS — Real-Time SOC Dashboard")

if alerts.empty:
    st.warning("No alerts yet. Start `realtime_detector.py`.")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔎 Filters")

protocols = sorted(alerts["protocol"].dropna().unique())
selected_protocols = st.sidebar.multiselect(
    "Protocol",
    options=protocols,
    default=protocols
)

min_risk, max_risk = int(alerts["final_risk"].min()), int(alerts["final_risk"].max())
risk_range = st.sidebar.slider(
    "Risk Range",
    min_value=0,
    max_value=100,
    value=(min_risk, max_risk)
)

filtered = alerts[
    (alerts["protocol"].isin(selected_protocols)) &
    (alerts["final_risk"] >= risk_range[0]) &
    (alerts["final_risk"] <= risk_range[1])
]

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Alerts", len(filtered))
c2.metric("High Risk", len(filtered[filtered["final_risk"] >= 70]))
c3.metric("Medium Risk", len(filtered[(filtered["final_risk"] >= 50) & (filtered["final_risk"] < 70)]))
c4.metric("Low Risk", len(filtered[filtered["final_risk"] < 50]))

st.divider()

# ---------------- TIMELINE REPLAY ----------------
st.subheader("⏱️ Attack Timeline Replay")

min_t = filtered["timestamp"].min()
max_t = filtered["timestamp"].max()

replay_t = st.slider(
    "Replay up to time",
    min_value=float(min_t),
    max_value=float(max_t),
    value=float(max_t),
    step=1.0
)

timeline_df = filtered[filtered["timestamp"] <= replay_t]

st.line_chart(
    timeline_df.set_index("time")[["final_risk"]],
    height=260
)

# ---------------- ALERT TABLE ----------------
st.subheader("🚨 Live Alerts")

table_df = timeline_df.copy()
table_df["Severity"] = table_df["final_risk"].apply(severity_color)

st.dataframe(
    table_df[[
        "time",
        "flow",
        "protocol",
        "final_risk",
        "Severity",
        "ml_prob",
        "stat_score",
        "iforest_risk"
    ]].sort_values("final_risk", ascending=False),
    height=400,
    use_container_width=True
)

# ---------------- FOOTER ----------------
st.markdown("""
### ℹ️ Notes
- 🔴 **High** → Likely covert channel
- 🟡 **Medium** → Suspicious timing pattern
- 🟢 **Low** → Normal traffic
- Timeline replay lets you **reconstruct attacks**
- Auto-blocking works only on **Linux (iptables)**
""")
