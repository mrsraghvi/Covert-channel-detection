# models/feature_importance.py
import joblib, numpy as np, pandas as pd, json, sys
from sklearn.preprocessing import StandardScaler

def main(model_path="models/rf_detector.joblib", features_json=None, topk=20):
    art = joblib.load(model_path)
    model = art['model']
    cols = art['columns']
    importances = model.feature_importances_
    pairs = sorted(zip(cols, importances), key=lambda x: x[1], reverse=True)
    print("Top features:")
    for name, imp in pairs[:topk]:
        print(f"{name:25s} {imp:.4f}")
    if features_json:
        with open(features_json) as f:
            feats = json.load(f)
        df = pd.DataFrame(feats)
        print("\nFeature sample stats:")
        print(df[cols].describe().T.head(topk))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/rf_detector.joblib")
    parser.add_argument("--features")
    parser.add_argument("--topk", type=int, default=20)
    args = parser.parse_args()
    main(args.model, args.features, args.topk)
