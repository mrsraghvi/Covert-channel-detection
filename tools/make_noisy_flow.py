# tools/make_noisy_flow.py
import pandas as pd, os, argparse
from preprocess.ipd_cleaning import apply_synthetic_jitter, compute_ipd, rescale_timestamps

def main(flow_csv, out_csv=None, jitter_std=0.01):
    df = pd.read_csv(flow_csv)
    df = compute_ipd(df, ts_col='ts')
    df = apply_synthetic_jitter(df, ipd_col='ipd', jitter_std=jitter_std)
    df = rescale_timestamps(df, ts_col='ts', start_at_zero=True)
    if out_csv is None:
        out_csv = flow_csv.replace(".csv", f"_noisy_j{int(jitter_std*1000)}.csv")
    df.to_csv(out_csv, index=False)
    print("Wrote noisy flow:", out_csv)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_csv")
    parser.add_argument("--jitter", type=float, default=0.005)
    args = parser.parse_args()
    main(args.flow_csv, jitter_std=args.jitter)
