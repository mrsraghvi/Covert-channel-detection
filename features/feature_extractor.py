# features/feature_extractor.py
"""
Extracts statistical features from flows:
 - mean, std, median, min/max IPD
 - entropy
 - autocorrelation
Outputs JSON feature file.
"""
import os
import json
import argparse
import numpy as np
import pandas as pd
from scipy.stats import entropy

OUT_DIR = "features"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def entropy_ipd(arr, bins=16):
    arr = np.array(arr)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return 0.0

    hist, _ = np.histogram(arr, bins=bins, density=True)
    hist = hist + 1e-12
    return float(entropy(hist))

def autocorr(arr):
    arr = np.array(arr)
    if len(arr) < 2:
        return 0.0
    return float(np.corrcoef(arr[:-1], arr[1:])[0, 1])

def extract_windows(ipds, window, step):
    features = []
    for start in range(0, len(ipds), step):
        end = start + window
        win = ipds[start:end]
        if len(win) == 0:
            break

        f = {
            "mean_ipd": float(np.mean(win)),
            "std_ipd": float(np.std(win)),
            "median_ipd": float(np.median(win)),
            "max_ipd": float(np.max(win)),
            "min_ipd": float(np.min(win)),
            "entropy_ipd": entropy_ipd(win),
            "autocorr": autocorr(win),
            "pkt_count": len(win)
        }
        features.append(f)

        if end >= len(ipds):
            break
    return features

def process_flow(flow_csv, window=50, step=25):
    df = pd.read_csv(flow_csv)
    ipds = df["ipd"].values
    feats = extract_windows(ipds, window, step)

    for f in feats:
        f["flow"] = os.path.basename(flow_csv)

    return feats

def main(args):
    ensure_dir()

    all_feats = []
    for f in args.flows:
        all_feats.extend(process_flow(f, args.window, args.step))

    out_json = os.path.join(OUT_DIR, f"features_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_json, "w") as fh:
        json.dump(all_feats, fh, indent=2)

    print(f"[+] Extracted {len(all_feats)} windows → {out_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("flows", nargs="+")
    parser.add_argument("--window", type=int, default=50)
    parser.add_argument("--step", type=int, default=25)
    args = parser.parse_args()
    main(args)
