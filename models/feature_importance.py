# models/feature_importance.py
"""
Print feature importance for the trained RandomForest model.
"""

import argparse
import json
import joblib
import pandas as pd
import numpy as np
import os

def main(features_json, model_path="models/rf_detector.joblib", topk=20):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    # Load model artifact
    artifact = joblib.load(model_path)
    model = artifact["model"]
    columns = artifact["columns"]

    # Load features (for stats only)
    with open(features_json, "r") as f:
        feats = json.load(f)

    df = pd.DataFrame(feats)

    # Feature importances
    importances = model.feature_importances_
    pairs = sorted(zip(columns, importances), key=lambda x: x[1], reverse=True)

    print("\nTop Feature Importances:\n" + "-" * 35)
    for name, imp in pairs[:topk]:
        print(f"{name:30s} {imp:.4f}")

    print("\nFeature Statistics (top features):\n" + "-" * 35)
    stats = df[columns].describe().T
    print(stats.loc[[p[0] for p in pairs[:topk]]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True, help="features_*.json file")
    parser.add_argument("--model", default="models/rf_detector.joblib")
    parser.add_argument("--topk", type=int, default=20)
    args = parser.parse_args()

    main(args.features, args.model, args.topk)
