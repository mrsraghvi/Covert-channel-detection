# fusion/risk_engine.py
"""
Final Fusion Engine:
Combines
- Phase 1: ML (Random Forest)
- Phase 2: Statistical tests
- Phase 4: Isolation Forest
into one final IDS risk score.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# -------------------------------------------------
# Ensure project root on PYTHONPATH
# -------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------
def load_ml_predictions(features_json, model_path):
    artifact = joblib.load(model_path)
    model = artifact["model"]
    columns = artifact["columns"]

    with open(features_json, "r") as f:
        feats = json.load(f)

    df = pd.DataFrame(feats)
    X = df[columns]

    probs = model.predict_proba(X)[:, 1] * 100

    return pd.DataFrame({
        "flow": df["flow"],
        "window_start": df["window_start"],
        "window_end": df["window_end"],
        "ml_prob": probs
    })

# -------------------------------------------------
def load_stat_scores(stat_json):
    with open(stat_json, "r") as f:
        stats = json.load(f)

    return pd.DataFrame(stats)[[
        "flow",
        "window_start",
        "window_end",
        "suspicion_score",
        "ks_pvalue",
        "ad_stat",
        "js_divergence"
    ]]

# -------------------------------------------------
def load_iforest_scores(iforest_csv):
    df = pd.read_csv(iforest_csv)
    return df[[
        "flow",
        "window_start",
        "window_end",
        "iforest_risk"
    ]]

# -------------------------------------------------
def fuse_scores(ml_df, stat_df, if_df):
    merged = ml_df.merge(
        stat_df,
        on=["flow", "window_start", "window_end"],
        how="inner"
    ).merge(
        if_df,
        on=["flow", "window_start", "window_end"],
        how="inner"
    )

    # Final weighted risk
    merged["final_risk"] = (
        0.50 * merged["ml_prob"] +
        0.30 * merged["suspicion_score"] +
        0.20 * merged["iforest_risk"]
    )

    # Decision
    def label(score):
        if score < 30:
            return "Normal"
        elif score < 60:
            return "Suspicious"
        else:
            return "Likely Covert"

    merged["decision"] = merged["final_risk"].apply(label)
    return merged

# -------------------------------------------------
def explain(row):
    reasons = []

    if row["ml_prob"] > 70:
        reasons.append("ML model strongly predicts covert behavior")

    if row["suspicion_score"] > 40:
        reasons.append("Statistical tests indicate abnormal timing")

    if row["iforest_risk"] > 60:
        reasons.append("Unsupervised model flags anomalous behavior")

    return "; ".join(reasons) if reasons else "No strong anomaly detected"

# -------------------------------------------------
def main(features_json, stat_json, iforest_csv, model_path):
    ml_df = load_ml_predictions(features_json, model_path)
    stat_df = load_stat_scores(stat_json)
    if_df = load_iforest_scores(iforest_csv)

    fused = fuse_scores(ml_df, stat_df, if_df)
    fused["explanation"] = fused.apply(explain, axis=1)

    os.makedirs("fusion_output", exist_ok=True)
    out = "fusion_output/final_risk_report.csv"
    fused.to_csv(out, index=False)

    print(f"[+] Final fused risk report saved → {out}")
    print("\nTop Alerts:\n" + "-" * 40)
    print(
        fused.sort_values("final_risk", ascending=False)
        .head(5)[["flow", "final_risk", "decision", "explanation"]]
    )

# -------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True)
    parser.add_argument("--stats", required=True)
    parser.add_argument("--iforest", required=True)
    parser.add_argument("--model", default="models/rf_detector.joblib")
    args = parser.parse_args()

    main(args.features, args.stats, args.iforest, args.model)
