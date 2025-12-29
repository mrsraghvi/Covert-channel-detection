# models/model_utils.py
"""
Helpers to load saved model and score new feature JSON.
"""
import joblib
import pandas as pd
import numpy as np

def load_model(path="models/rf_detector.joblib"):
    d = joblib.load(path)
    return d["model"], d["scaler"], d["columns"]

def score_features_json(features_json, model_path="models/rf_detector.joblib"):
    import json
    with open(features_json) as f:
        feats = json.load(f)
    df = pd.DataFrame(feats)
    model, scaler, cols = load_model(model_path)
    X = df[cols].fillna(0)
    Xs = scaler.transform(X)
    probs = model.predict_proba(Xs)[:,1]
    df["prob_covert"] = probs
    return df
