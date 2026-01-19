# features/feature_extractor.py
import argparse
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from feature_utils import (
    fft_features,
    autocorr_features,
    entropy_features
)

# =========================================================
# Basic Statistical Features
# =========================================================
def basic_features(ipd):
    return {
        "ipd_mean": float(np.mean(ipd)),
        "ipd_std": float(np.std(ipd)),
        "ipd_min": float(np.min(ipd)),
        "ipd_max": float(np.max(ipd)),
        "ipd_median": float(np.median(ipd)),
        "ipd_iqr": float(np.percentile(ipd, 75) - np.percentile(ipd, 25))
    }

# =========================================================
# Feature Extraction Per Window
# =========================================================
def extract_window_features(df, window_size, step_size, flow_name):
    features = []

    ipd = df["ipd"].values

    for start in range(0, len(ipd) - window_size + 1, step_size):
        end = start + window_size
        ipd_window = ipd[start:end]

        feat = {
            "flow": flow_name,
            "window_start": start,
            "window_end": end
        }

        # Basic stats
        feat.update(basic_features(ipd_window))

        # Advanced features (PHASE 1)
        feat.update(fft_features(ipd_window))
        feat.update(autocorr_features(ipd_window))
        feat.update(entropy_features(ipd_window))

        features.append(feat)

    return features

# =========================================================
# Main
# =========================================================
def main():
    parser = argparse.ArgumentParser(description="Extract IPD-based features")
    parser.add_argument("flow_files", nargs="+", help="CSV flow files")
    parser.add_argument("--window", type=int, default=50, help="Window size")
    parser.add_argument("--step", type=int, default=25, help="Step size")
    args = parser.parse_args()

    all_features = []

    for flow_file in args.flow_files:
        df = pd.read_csv(flow_file)

        if "ipd" not in df.columns:
            raise ValueError(f"'ipd' column missing in {flow_file}")

        flow_name = os.path.basename(flow_file).replace(".csv", "")
        feats = extract_window_features(
            df,
            window_size=args.window,
            step_size=args.step,
            flow_name=flow_name
        )
        all_features.extend(feats)

    if not all_features:
        raise RuntimeError("No features extracted")

    os.makedirs("features", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"features/features_{ts}.json"

    with open(out_path, "w") as f:
        json.dump(all_features, f, indent=2)

    print(f"[+] Extracted {len(all_features)} windows → {out_path}")

if __name__ == "__main__":
    main()
