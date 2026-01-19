# features/stat_feature_extractor.py
"""
Extract statistical test features per IPD window.
Phase 2 — Statistical Detection (Explainable).
"""

import os
import sys

# -------------------------------------------------
# Ensure project root is on PYTHONPATH (PERMANENT FIX)
# -------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------
import argparse
import json
from datetime import datetime
import pandas as pd
import numpy as np

from stats.stat_tests import (
    ks_test,
    ad_test,
    js_divergence,
    suspicion_score
)

# -------------------------------------------------
def extract_stat_features(df, window, step, flow_name, baseline_ipd):
    results = []
    ipd = df["ipd"].values

    for start in range(0, len(ipd) - window + 1, step):
        end = start + window
        w = ipd[start:end]

        ks_stat, ks_p = ks_test(w, baseline_ipd)
        ad_stat = ad_test(w)
        jsd = js_divergence(w, baseline_ipd)
        score = suspicion_score(ks_stat, ks_p, ad_stat, jsd)

        results.append({
            "flow": flow_name,
            "window_start": start,
            "window_end": end,
            "ks_stat": ks_stat,
            "ks_pvalue": ks_p,
            "ad_stat": ad_stat,
            "js_divergence": jsd,
            "suspicion_score": score
        })

    return results

# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline_flow", help="Normal traffic flow CSV")
    parser.add_argument("target_flows", nargs="+", help="Flows to test")
    parser.add_argument("--window", type=int, default=50)
    parser.add_argument("--step", type=int, default=25)
    args = parser.parse_args()

    baseline_df = pd.read_csv(args.baseline_flow)
    baseline_ipd = baseline_df["ipd"].values

    all_results = []

    for flow_file in args.target_flows:
        df = pd.read_csv(flow_file)
        flow_name = os.path.basename(flow_file).replace(".csv", "")
        feats = extract_stat_features(
            df,
            args.window,
            args.step,
            flow_name,
            baseline_ipd
        )
        all_results.extend(feats)

    os.makedirs("stats_output", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"stats_output/stat_features_{ts}.json"

    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"[+] Extracted {len(all_results)} stat windows → {out}")

# -------------------------------------------------
if __name__ == "__main__":
    main()
