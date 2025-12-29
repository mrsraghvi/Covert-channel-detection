# dashboard/app.py
"""
Streamlit dashboard to inspect flows, IPD time-series and model scores.
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from models.model_utils import load_model, score_features_json

st.set_page_config(layout="wide", page_title="Covert Timing Channel Detector")

st.title("Covert Timing Channel Detector — Dashboard")

# Left: upload or pick capture / flows
st.sidebar.header("Data")
upload = st.sidebar.file_uploader("Upload capture CSV (optional)", type=["csv"])
use_preprocessed = st.sidebar.checkbox("Use preprocessed/flows CSVs (recommended)", value=True)

if upload:
    df_capture = pd.read_csv(upload)
    st.sidebar.success("Uploaded capture")
else:
    df_capture = None

if use_preprocessed:
    flow_files = glob.glob("preprocessed/flows/*.csv")
    flow_files.sort()
    flow_sel = st.sidebar.selectbox("Choose a flow CSV", ["-- none --"] + flow_files)
else:
    flow_sel = None

st.sidebar.header("Model")
model_path = st.sidebar.text_input("Model path", value="models/rf_detector.joblib")
st.sidebar.write("Model:", model_path)

if st.sidebar.button("Reload model"):
    try:
        model, scaler, cols = load_model(model_path)
        st.sidebar.success("Model loaded")
    except Exception as e:
        st.sidebar.error(f"Load error: {e}")

# Main panel
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Flow IPD")
    if flow_sel and flow_sel != "-- none --":
        df_flow = pd.read_csv(flow_sel)
        st.write("Flow file:", flow_sel)
        st.line_chart(df_flow["ipd"].fillna(0).values)
        st.write(df_flow.head())
    elif df_capture is not None:
        st.write("Capture preview")
        st.dataframe(df_capture.head())

with col2:
    st.header("Model Scores")
    features_glob = sorted(glob.glob("features/*.json"))
    feat_sel = st.selectbox("Choose features JSON", ["-- none --"] + features_glob)
    if feat_sel and feat_sel != "-- none --":
        scored = score_features_json(feat_sel, model_path=model_path)
        st.write("Top windows by covert probability")
        st.dataframe(scored.sort_values("prob_covert", ascending=False).head(20))
        st.bar_chart(scored["prob_covert"].values)

st.write("Tips: generate data with sender/sender_simulator.py for quick tests, then run preprocess/feature extraction and train models.")
