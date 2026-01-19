# live/live_logger.py
"""
Continuous live packet logger for covert timing analysis
"""

import time
import csv
from collections import defaultdict, deque
from scapy.all import sniff, IP

LOG_FILE = "live/live_ipd_log.csv"
WINDOW_SIZE = 50

buffers = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))

# Initialize CSV
with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "flow", "ipd"])

last_seen = {}

def handle_packet(pkt):
    if IP not in pkt:
        return

    flow = f"{pkt[IP].src}_{pkt[IP].dst}_{pkt.proto}"
    now = time.time()

    if flow in last_seen:
        ipd = now - last_seen[flow]
        buffers[flow].append(ipd)

        # Log continuously
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([now, flow, ipd])

    last_seen[flow] = now

def start_live_capture():
    print("[+] Starting continuous packet capture...")
    sniff(prn=handle_packet, store=False)

if __name__ == "__main__":
    start_live_capture()
