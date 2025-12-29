# sender/sender_simulator.py
"""
Synthetic packet generator for testing covert timing channel detection.
Creates:
 - A normal flow (random inter-arrival times)
 - A covert flow (timing-based bit encoding)
Outputs CSV: sender_output/<timestamp>_packets.csv
NO ADMIN RIGHTS NEEDED.
"""
import os
import csv
import time
import argparse
import random
from datetime import datetime

OUT_DIR = "sender_output"

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def generate_normal_flow(start_ts, n_pkts=500, rate=50, src="10.0.0.1", dst="10.0.0.2"):
    """
    Normal traffic using exponential inter-arrival times.
    """
    ts = start_ts
    rows = []
    for _ in range(n_pkts):
        ipd = random.expovariate(rate)       # exponential IPD
        ts += ipd
        rows.append((ts, src, dst, 40000, 80, "TCP", random.randint(60, 1500)))
    return rows

def generate_covert_flow(start_ts, bits="1011001", repeat=40, src="10.0.0.3", dst="10.0.0.4"):
    """
    Covert timing channel: short delay = '0', long delay = '1'
    """
    SHORT = 0.02
    LONG  = 0.12

    ts = start_ts
    rows = []
    for _ in range(repeat):
        for b in bits:
            ts += 0.001                      # packet timestamp
            rows.append((ts, src, dst, 0, 0, "ICMP", 64))

            # Encode bit using timing
            ts += random.uniform(SHORT*0.9, SHORT*1.1) if b == "0" else \
                  random.uniform(LONG*0.9, LONG*1.1)

        ts += random.uniform(0.2, 0.4)       # gap between sequences
    return rows

def write_csv(rows, out_path):
    """
    Write packet rows to CSV.
    """
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","src","dst","sport","dport","proto","length"])
        w.writerows(rows)

def main(args):
    ensure_dir()
    t0 = time.time()

    # Generate normal + covert traffic
    normal = generate_normal_flow(t0, n_pkts=args.normal_pkts, rate=args.rate)
    covert = generate_covert_flow(t0, bits=args.bits, repeat=args.repeat)

    # Combine & sort
    all_rows = sorted(normal + covert, key=lambda x: x[0])

    # Save output
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUT_DIR, f"{ts_str}_packets.csv")
    write_csv(all_rows, out_path)

    print(f"[+] Generated {len(all_rows)} packets → {out_path}")
    print("[!] Use this file with capture_from_csv.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", default="1011001", help="Covert bitstring")
    parser.add_argument("--repeat", type=int, default=40, help="Repeat bitstring")
    parser.add_argument("--normal_pkts", type=int, default=1000, help="Normal traffic packets")
    parser.add_argument("--rate", type=float, default=30, help="Normal traffic avg packet/s")
    args = parser.parse_args()
    main(args)
