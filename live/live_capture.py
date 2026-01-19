# live/live_capture.py
"""
Real-time packet capture for covert timing detection
"""

import time
import pandas as pd
from scapy.all import sniff, IP
from collections import defaultdict

packets = defaultdict(list)

def handle_packet(pkt):
    if IP in pkt:
        flow = f"{pkt[IP].src}_{pkt[IP].dst}"
        packets[flow].append(time.time())

def start_capture(duration=30):
    print(f"[+] Capturing live traffic for {duration} seconds...")
    sniff(prn=handle_packet, timeout=duration)

    rows = []
    for flow, times in packets.items():
        for i in range(1, len(times)):
            rows.append({
                "flow": flow,
                "ts": times[i],
                "ipd": times[i] - times[i-1]
            })

    df = pd.DataFrame(rows)
    df.to_csv("live/live_ipd.csv", index=False)
    print("[+] Live IPD data saved → live/live_ipd.csv")

if __name__ == "__main__":
    start_capture()
