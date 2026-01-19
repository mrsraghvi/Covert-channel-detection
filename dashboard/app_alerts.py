# dashboard/app_alerts.py
"""
SOC-style IDS Alerts Dashboard
Reads fusion_output/final_risk_report.csv
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Covert Channel IDS Alerts",
    layout="wide"
)

st.title("🚨 Covert Timing Channel — IDS Alerts")

DATA_PATH = "fusion_output/final_risk_report.csv"

if not os.path.exists(DATA_PATH):
    st.error("❌ No fused risk report found. Run fusion/risk_engine.py first.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# -------------------------------------------------
# Sidebar filters
# -------------------------------------------------
st.sidebar.header("Filters")

risk_range = st.sidebar.slider(
    "Risk Score Range",
    0, 100, (0, 100)
)

decision_filter = st.sidebar.multiselect(
    "Decision",
    options=df["decision"].unique().tolist(),
    default=df["decision"].unique().tolist()
)

df_filt = df[
    (df["final_risk"] >= risk_range[0]) &
    (df["final_risk"] <= risk_range[1]) &
    (df["decision"].isin(decision_filter))
]

# -------------------------------------------------
# Summary metrics
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Windows", len(df))
c2.metric("🟢 Normal", (df["decision"] == "Normal").sum())
c3.metric("🟡 Suspicious", (df["decision"] == "Suspicious").sum())
c4.metric("🔴 Likely Covert", (df["decision"] == "Likely Covert").sum())

st.markdown("---")

# -------------------------------------------------
# Alert cards
# -------------------------------------------------
st.subheader("Active Alerts")

alerts = df_filt.sort_values("final_risk", ascending=False)

if alerts.empty:
    st.success("No alerts in selected range.")
else:
    for _, row in alerts.head(5).iterrows():
        risk = row["final_risk"]

        if risk >= 60:
            color = "🔴"
        elif risk >= 30:
            color = "🟡"
        else:
            color = "🟢"

        st.markdown(
            f"""
            ### {color} {row['decision']}
            **Flow:** `{row['flow']}`  
            **Risk Score:** `{risk:.2f}`  

            **ML Probability:** `{row['ml_prob']:.2f}`  
            **Statistical Suspicion:** `{row['suspicion_score']:.2f}`  

            **Explanation:**  
            {row['explanation']}
            ---
            """
        )

# -------------------------------------------------
# Full table
# -------------------------------------------------
st.subheader("Full Detection Report")

st.dataframe(
    df_filt[
        [
            "flow",
            "window_start",
            "window_end",
            "ml_prob",
            "suspicion_score",
            "final_risk",
            "decision",
            "explanation",
        ]
    ].sort_values("final_risk", ascending=False),
    use_container_width=True,
)
