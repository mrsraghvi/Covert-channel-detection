# create_eval_files.ps1
Set-StrictMode -Version Latest

# ensure directories exist
New-Item -ItemType Directory -Path .\models -Force | Out-Null
New-Item -ItemType Directory -Path .\tools -Force | Out-Null

# Write models/eval_cv.py
@'
# models/eval_cv.py
import json, numpy as np, pandas as pd, joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, roc_curve
import matplotlib.pyplot as plt
import sys, os

def load_features(json_path):
    with open(json_path) as f:
        feats = json.load(f)
    df = pd.DataFrame(feats)
    df['label'] = df['flow'].apply(lambda x: 1 if "10.0.0.3" in x or "10.0.0.4" in x else 0)
    X = df.drop(columns=['flow','window_start','window_end','label'], errors='ignore').fillna(0)
    y = df['label'].values
    return X, y, df

def run_cv(json_path, n_splits=5):
    X, y, df = load_features(json_path)
    if len(np.unique(y)) < 2:
        print("Only one class present; cannot run CV.")
        return
    skf = StratifiedKFold(n_splits=min(n_splits, max(2, sum(y))), shuffle=True, random_state=42)
    aucs = []
    fold = 0
    for train_idx, test_idx in skf.split(X, y):
        fold += 1
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        scaler = StandardScaler().fit(X_train)
        Xtr = scaler.transform(X_train); Xte = scaler.transform(X_test)
        clf = RandomForestClassifier(n_estimators=150, random_state=42)
        clf.fit(Xtr, y_train)
        probs = clf.predict_proba(Xte)[:,1]
        try:
            a = roc_auc_score(y_test, probs)
        except Exception:
            a = float('nan')
        aucs.append(a)
        print(f"Fold {fold}: AUC={a:.4f}")
        print(classification_report(y_test, clf.predict(Xte)))
    print(f"Mean AUC: {np.nanmean(aucs):.4f} (+/- {np.nanstd(aucs):.4f})")
    # Optionally plot ROC using last fold
    try:
        fpr, tpr, _ = roc_curve(y_test, probs)
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC (AUC={a:.3f})')
        plt.plot([0,1],[0,1],'--',alpha=0.5)
        plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title('ROC Curve (last CV fold)')
        plt.legend()
        plt.show()
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python models/eval_cv.py features/<file>.json")
        sys.exit(1)
    run_cv(sys.argv[1], n_splits=5)
'@ > .\models\eval_cv.py

# Write models/feature_importance.py
@'
# models/feature_importance.py
import joblib, json, pandas as pd
import argparse

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/rf_detector.joblib")
    parser.add_argument("--features")
    parser.add_argument("--topk", type=int, default=20)
    args = parser.parse_args()
    main(args.model, args.features, args.topk)
'@ > .\models\feature_importance.py

# Write tools/make_noisy_flow.py
@'
# tools/make_noisy_flow.py
import pandas as pd
import argparse
from preprocess.ipd_cleaning import compute_ipd, apply_synthetic_jitter, rescale_timestamps
import os

def main(flow_csv, out_csv=None, jitter_std=0.01):
    df = pd.read_csv(flow_csv)
    # recompute ipd if missing
    if "ipd" not in df.columns:
        df = compute_ipd(df, ts_col='ts')
    df_noisy = apply_synthetic_jitter(df, ipd_col='ipd', jitter_std=jitter_std)
    # optionally rescale timestamps to start at zero
    df_noisy = rescale_timestamps(df_noisy, ts_col='ts', start_at_zero=True)
    if out_csv is None:
        base = os.path.splitext(flow_csv)[0]
        out_csv = f"{base}_noisy_j{int(jitter_std*1000)}.csv"
    df_noisy.to_csv(out_csv, index=False)
    print("[+] Wrote noisy flow:", out_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_csv")
    parser.add_argument("--jitter", type=float, default=0.005)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    main(args.flow_csv, args.out, args.jitter)
'@ > .\tools\make_noisy_flow.py

Write-Host "Created: models\eval_cv.py"
Write-Host "Created: models\feature_importance.py"
Write-Host "Created: tools\make_noisy_flow.py"
Write-Host "Done."
