# models/iforest_detect.py
"""
Phase 4: Use Isolation Forest to score anomaly risk
"""

import json
import joblib
import argparse
import pandas as pd
import numpy as np

def main(features_json, model_path):
    artifact = joblib.load(model_path)
    model = artifact["model"]
    columns = artifact["columns"]

    with open(features_json, "r") as f:
        feats = json.load(f)

    df = pd.DataFrame(feats)
    X = df[columns]

    # Isolation Forest:
    # score_samples → higher = more normal
    scores = model.score_samples(X)

    # Convert to anomaly risk (0–100)
    risk = (1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)) * 100

    df["iforest_risk"] = risk

    out = "models/iforest_scores.csv"
    df[
        ["flow", "window_start", "window_end", "iforest_risk"]
    ].to_csv(out, index=False)

    print(f"[+] Isolation Forest risk scores saved → {out}")
    print(df.sort_values("iforest_risk", ascending=False).head(5))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("features", help="features_*.json")
    parser.add_argument("--model", default="models/iforest_detector.joblib")
    args = parser.parse_args()

    main(args.features, args.model)
