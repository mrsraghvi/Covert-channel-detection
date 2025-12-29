# preprocess/parse_pcap.py
"""
Higher-level pcap parsing + metadata extraction.
Wraps capture_from_pcap and produces a pandas dataframe for downstream steps.
"""
import pandas as pd
import argparse
from capture.capture_from_pcap import pcap_to_csv

def parse_pcap_to_df(pcap_path, csv_out=None):
    csv_path = pcap_to_csv(pcap_path, out_csv=csv_out)
    df = pd.read_csv(csv_path)
    df = df.sort_values("ts").reset_index(drop=True)
    return df, csv_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    args = parser.parse_args()
    df, csv_path = parse_pcap_to_df(args.pcap)
    print(df.head())
