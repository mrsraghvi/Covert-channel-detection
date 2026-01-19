# models/iforest_train.py
"""
Phase 4: Train Isolation Forest on NORMAL traffic only
"""

import json
import joblib
import argparse
import pandas as pd
from sklearn.ensemble import IsolationForest
import os

def main(features_json, out_model="models/iforest_detector.joblib"):
    with open(features_json, "r") as f:
        feats = json.load(f)

    df = pd.DataFrame(feats)

    # Remove non-feature columns
    non_features = ["flow", "window_start", "window_end", "label"]
    X = df.drop(columns=[c for c in non_features if c in df.columns])

    print(f"[+] Training Isolation Forest on {len(X)} windows")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.1,   # expected anomaly ratio
        random_state=42
    )

    model.fit(X)

    os.makedirs("models", exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "columns": X.columns.tolist()
        },
        out_model
    )

    print(f"[+] Isolation Forest model saved → {out_model}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("features", help="features_*.json (NORMAL traffic)")
    parser.add_argument("--out", default="models/iforest_detector.joblib")
    args = parser.parse_args()

    main(args.features, args.out)
