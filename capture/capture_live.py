# capture/capture_live.py
"""
Live capture utility using scapy.sniff. Captures packets and writes a CSV.
Requires admin privileges on many platforms.
If you cannot run live capture, use capture_from_pcap.py to parse pcap files.
"""
import argparse
import csv
import os
from scapy.all import sniff
import time

OUT_DIR = "capture"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def packet_to_row(pkt):
    # Try to extract common fields; tolerate missing ones
    ts = float(pkt.time)
    src = pkt[0].src if hasattr(pkt[0], "src") else None
    dst = pkt[0].dst if hasattr(pkt[0], "dst") else None
    proto = pkt.proto if hasattr(pkt, "proto") else pkt.name
    sport = pkt.sport if hasattr(pkt, "sport") else None
    dport = pkt.dport if hasattr(pkt, "dport") else None
    length = len(pkt)
    return [ts, src, dst, sport, dport, proto, length]

def capture_to_csv(interface=None, timeout=None, count=None):
    ensure_dir()
    rows = []
    def cb(pkt):
        rows.append(packet_to_row(pkt))
    sniff(iface=interface, prn=cb, timeout=timeout, count=count)
    out = os.path.join(OUT_DIR, f"capture_{int(time.time())}.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","src","dst","sport","dport","proto","length"])
        w.writerows(rows)
    print(f"[+] Captured {len(rows)} packets → {out}")
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iface", help="capture interface (optional)")
    parser.add_argument("--timeout", type=int, help="capture timeout (seconds)", default=10)
    parser.add_argument("--count", type=int, help="max packet count", default=None)
    args = parser.parse_args()
    print("WARNING: live capture may require admin privileges. Run in lab only.")
    capture_to_csv(interface=args.iface, timeout=args.timeout, count=args.count)
