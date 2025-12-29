# models/train_model.py
"""
Train & evaluate models. Uses a simple labeling heuristic for simulated data:
 - flow filename containing '10.0.0.3' -> covert (1), else normal (0)
Saves model + scaler + columns as joblib.
"""
import os
import json
import joblib
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def load_features_json(json_path):
    with open(json_path) as f:
        feats = json.load(f)
    df = pd.DataFrame(feats)
    df["label"] = df["flow"].apply(lambda x: 1 if "10.0.0.3" in x or "10.0.0.4" in x else 0)
    X = df.drop(columns=["flow", "window_start", "window_end", "label"], errors="ignore")
    X = X.fillna(0)
    y = df["label"].values
    return X, y

def train(json_path, out_model=None):
    X, y = load_features_json(json_path)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.25, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=150, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:,1]
    print(classification_report(y_test, preds))
    try:
        auc = roc_auc_score(y_test, probs)
        print(f"AUC: {auc:.4f}")
    except Exception:
        pass
    model_art = {
        "model": clf,
        "scaler": scaler,
        "columns": list(X.columns)
    }
    if out_model is None:
        out_model = os.path.join(MODEL_DIR, "rf_detector.joblib")
    joblib.dump(model_art, out_model)
    print(f"[+] Saved model → {out_model}")
    return out_model

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("features_json")
    parser.add_argument("--out", help="model output path", default=None)
    args = parser.parse_args()
    train(args.features_json, args.out)
