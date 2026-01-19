# tools/make_noisy_flow.py
"""
Create a noisy version of a flow CSV by adding synthetic jitter to IPDs.
Permanent fix: ensures project root is added to sys.path so imports work
in CMD, PowerShell, VS Code, and scripts.
"""

import os
import sys

# ---------------------------------------------------------
# Ensure project root is on PYTHONPATH
# ---------------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import argparse

from preprocess.ipd_cleaning import (
    compute_ipd,
    apply_synthetic_jitter,
    rescale_timestamps
)

# ---------------------------------------------------------
# Main logic
# ---------------------------------------------------------
def main(flow_csv, jitter_std=0.01, out_csv=None):
    df = pd.read_csv(flow_csv)

    # Ensure IPD exists
    if "ipd" not in df.columns:
        df = compute_ipd(df, ts_col="ts")

    # Apply jitter
    df = apply_synthetic_jitter(df, ipd_col="ipd", jitter_std=jitter_std)

    # Rebuild timestamps
    df = rescale_timestamps(df, ts_col="ts", start_at_zero=True)

    # Output filename
    if out_csv is None:
        base = os.path.splitext(flow_csv)[0]
        out_csv = f"{base}_noisy_j{int(jitter_std * 1000)}.csv"

    df.to_csv(out_csv, index=False)
    print(f"[+] Wrote noisy flow: {out_csv}")

# ---------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_csv", help="Input flow CSV")
    parser.add_argument("--jitter", type=float, default=0.01, help="Jitter std (seconds)")
    parser.add_argument("--out", default=None, help="Optional output CSV")
    args = parser.parse_args()

    main(args.flow_csv, args.jitter, args.out)
