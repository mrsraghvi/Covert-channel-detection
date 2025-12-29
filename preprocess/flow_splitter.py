# preprocess/flow_splitter.py
"""
Splits capture CSV into flows and computes IPDs.
Outputs: preprocessed/flows/*.csv
"""
import os
import argparse
import pandas as pd

OUT_DIR = "preprocessed/flows"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def split_flows(capture_csv):
    df = pd.read_csv(capture_csv)
    df = df.sort_values("ts").reset_index(drop=True)

    df["flow"] = df.apply(lambda r: f"{r.src}_{r.dst}_{r.proto}", axis=1)

    ensure_dir()
    flow_paths = []

    for flow, g in df.groupby("flow"):
        g = g.sort_values("ts").reset_index(drop=True)
        g["ipd"] = g["ts"].diff().fillna(0)

        out = os.path.join(OUT_DIR, f"{flow}.csv")
        g.to_csv(out, index=False)
        flow_paths.append(out)

    print(f"[+] Wrote {len(flow_paths)} flows → {OUT_DIR}")
    return flow_paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capture_csv")
    args = parser.parse_args()
    split_flows(args.capture_csv)
