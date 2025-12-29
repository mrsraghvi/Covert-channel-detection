# capture/capture_from_pcap.py
"""
Read a pcap (or pcapng) and convert to normalized CSV with timestamps and basic meta.
Uses scapy.rdpcap or pyshark if needed.
"""
import argparse
import os
import csv
from scapy.all import rdpcap

OUT_DIR = "capture"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def pcap_to_csv(pcap_path, out_csv=None):
    pkts = rdpcap(pcap_path)
    rows = []
    for p in pkts:
        try:
            ts = float(p.time)
            src = p[0].src if hasattr(p[0], "src") else None
            dst = p[0].dst if hasattr(p[0], "dst") else None
            sport = p.sport if hasattr(p, "sport") else None
            dport = p.dport if hasattr(p, "dport") else None
            proto = p.name
            length = len(p)
            rows.append([ts, src, dst, sport, dport, proto, length])
        except Exception:
            continue
    ensure_dir()
    if out_csv is None:
        out_csv = os.path.join(OUT_DIR, f"capture_{int(__import__('time').time())}.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","src","dst","sport","dport","proto","length"])
        w.writerows(rows)
    print(f"[+] Converted {len(rows)} packets → {out_csv}")
    return out_csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    parser.add_argument("--out", help="output csv path", default=None)
    args = parser.parse_args()
    pcap_to_csv(args.pcap, args.out)
