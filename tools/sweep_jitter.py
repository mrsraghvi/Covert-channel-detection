# tools/sweep_jitter.py  (improved - prints subprocess stdout/stderr on error)
import os
import sys
import subprocess
import time
import csv

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable

COVERT_FLOW = r"preprocessed/flows/10.0.0.3_10.0.0.4_ICMP.csv"
NORMAL_FLOW = r"preprocessed/flows/10.0.0.1_10.0.0.2_TCP.csv"
FEATURES_DIR = r"features"
RESULTS_DIR = r"results"

os.makedirs(FEATURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

JITTERS = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]

summary_rows = []

def run_cmd(cmd, cwd=REPO):
    """Run cmd (string) and return (success, stdout). On failure, return (False, combined_out)."""
    try:
        out = subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT)
        return True, out.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        out = e.output.decode("utf-8", errors="ignore") if getattr(e, "output", None) else str(e)
        return False, out

for j in JITTERS:
    tag = f"j{int(j*1000)}"
    print("="*60)
    print(f"Running jitter = {j} ({tag})")

    # 1) create noisy flow (if j==0 we just copy)
    if j == 0.0:
        noisy_flow = COVERT_FLOW
        print("  - j=0.0: using original covert flow (no noise)")
    else:
        noisy_flow = COVERT_FLOW.replace(".csv", f"_noisy_{tag}.csv")
        cmd = f'{PY} tools/make_noisy_flow.py "{COVERT_FLOW}" --jitter {j} --out "{noisy_flow}"'
        print("  - making noisy flow:", cmd)
        ok, out = run_cmd(cmd)
        if not ok:
            print("[!] make_noisy_flow failed:")
            print(out)
            # continue to next jitter level instead of crashing
            summary_rows.append({"jitter": j, "features": "", "mean_auc": "", "roc": "", "note": "make_noisy_flow failed"})
            continue
        print(out.strip().splitlines()[-3:])

    time.sleep(0.1)

    # 2) extract features for normal + noisy
    feat_cmd = f'{PY} features/feature_extractor.py "{NORMAL_FLOW}" "{noisy_flow}" --window 50 --step 25'
    print("  - extracting features:", feat_cmd)
    ok, out = run_cmd(feat_cmd)
    if not ok:
        print("[!] feature_extractor failed:")
        print(out)
        summary_rows.append({"jitter": j, "features": "", "mean_auc": "", "roc": "", "note": "feature_extractor failed"})
        continue
    print(out.strip().splitlines()[-3:])

    # find newest features JSON
    feats = sorted([f for f in os.listdir(FEATURES_DIR) if f.startswith("features_") and f.endswith(".json")],
                   key=lambda x: os.path.getmtime(os.path.join(FEATURES_DIR, x)))
    if not feats:
        print("[!] No features JSON found after extraction.")
        summary_rows.append({"jitter": j, "features": "", "mean_auc": "", "roc": "", "note": "no features json"})
        continue
    features_file = os.path.join(FEATURES_DIR, feats[-1])
    print("  - features file:", features_file)

    # 3) train model
    train_cmd = f'{PY} models/train_model.py "{features_file}"'
    print("  - training:", train_cmd)
    ok, tr_out = run_cmd(train_cmd)
    if not ok:
        print("[!] train_model failed:")
        print(tr_out)
        summary_rows.append({"jitter": j, "features": os.path.basename(features_file), "mean_auc": "", "roc": "", "note": "train failed"})
        continue
    print("\n".join(tr_out.strip().splitlines()[-6:]))

    # 4) run CV save (eval_cv_save.py saves ROC to results/)
    eval_cmd = f'{PY} models/eval_cv_save.py "{features_file}"'
    print("  - evaluating (CV + ROC save):", eval_cmd)
    ok, ev_out = run_cmd(eval_cmd)
    if not ok:
        print("[!] eval_cv_save failed:")
        print(ev_out)
        summary_rows.append({"jitter": j, "features": os.path.basename(features_file), "mean_auc": "", "roc": "", "note": "eval failed"})
        continue
    print(ev_out.strip().splitlines()[-6:])

    # parse Mean AUC
    mean_auc = ""
    for line in ev_out.splitlines():
        if "Mean AUC:" in line:
            try:
                mean_auc = float(line.split("Mean AUC:")[1].split()[0])
            except:
                mean_auc = ""

    # find ROC PNG
    rocs = sorted([f for f in os.listdir(RESULTS_DIR) if f.startswith("roc_") and f.endswith(".png")],
                  key=lambda x: os.path.getmtime(os.path.join(RESULTS_DIR, x)))
    roc_png = os.path.join(RESULTS_DIR, rocs[-1]) if rocs else ""

    summary_rows.append({"jitter": j, "features": os.path.basename(features_file),
                         "mean_auc": mean_auc, "roc": roc_png, "note": ""})

# write summary CSV
csv_path = os.path.join(RESULTS_DIR, "sweep_summary.csv")
with open(csv_path, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["jitter", "features", "mean_auc", "roc", "note"])
    w.writeheader()
    for r in summary_rows:
        w.writerow(r)

print("="*60)
print(f"Done. Summary saved to {csv_path}")
print("Results summary:")
for row in summary_rows:
    print(row)
