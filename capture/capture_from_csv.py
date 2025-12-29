# capture/capture_from_csv.py
"""
Converts simulator output to a normalized capture CSV.
"""
import os
import argparse
import pandas as pd
from datetime import datetime

OUT_DIR = "capture"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def normalize_csv(input_csv):
    df = pd.read_csv(input_csv)
    df['ts'] = df['ts'].astype(float)
    df = df.sort_values('ts').reset_index(drop=True)

    ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUT_DIR, f"capture_{ts}.csv")

    df.to_csv(out_path, index=False)
    print(f"[+] Normalized → {out_path}")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    args = parser.parse_args()
    normalize_csv(args.input_csv)
