# models/eval_cv_save.py
import json, numpy as np, pandas as pd, joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, roc_curve, auc
import matplotlib
matplotlib.use('Agg')   # use non-interactive backend
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

def run_cv(json_path, n_splits=5, out_dir="results"):
    os.makedirs(out_dir, exist_ok=True)
    X, y, df = load_features(json_path)
    if len(np.unique(y)) < 2:
        print("Only one class present; cannot run CV.")
        return
    skf = StratifiedKFold(n_splits=min(n_splits, max(2, sum(y))), shuffle=True, random_state=42)
    aucs = []
    fold = 0
    last_probs = None
    last_y_test = None
    for train_idx, test_idx in skf.split(X, y):
        fold += 1
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        scaler = StandardScaler().fit(X_train)
        Xtr = scaler.transform(X_train); Xte = scaler.transform(X_test)
        clf = RandomForestClassifier(n_estimators=150, random_state=42)
        clf.fit(Xtr, y_train)
        probs = clf.predict_proba(Xte)[:,1]
        last_probs = probs
        last_y_test = y_test
        try:
            a = roc_auc_score(y_test, probs)
        except Exception:
            a = float('nan')
        aucs.append(a)
        print(f"Fold {fold}: AUC={a:.4f}")
        print(classification_report(y_test, clf.predict(Xte)))
    print(f"Mean AUC: {np.nanmean(aucs):.4f} (+/- {np.nanstd(aucs):.4f})")

    # Save ROC for last fold
    try:
        fpr, tpr, _ = roc_curve(last_y_test, last_probs)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(6,6))
        plt.plot(fpr, tpr, label=f'ROC (AUC={roc_auc:.3f})')
        plt.plot([0,1],[0,1],'--',alpha=0.5)
        plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title('ROC Curve (last CV fold)')
        plt.legend()
        outpath = os.path.join(out_dir, f"roc_{os.path.basename(json_path).replace('.json','')}.png")
        plt.savefig(outpath, dpi=150, bbox_inches='tight')
        print(f"[+] Saved ROC plot → {outpath}")
    except Exception as e:
        print("Could not save ROC plot:", e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python models/eval_cv_save.py features/<file>.json")
        sys.exit(1)
    run_cv(sys.argv[1], n_splits=5)
