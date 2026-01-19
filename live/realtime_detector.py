# live/realtime_detector.py
"""
Real-Time Covert Channel Detector with:
- Protocol-aware labeling (TCP, UDP, ICMP, HTTP, HTTPS, SSL)
- Risk-based alerting
- Platform-safe auto-blocking (Linux real / Windows simulated)
"""

import time
import csv
import os
import platform
import subprocess
import joblib
import numpy as np
import pandas as pd
from collections import defaultdict
from scapy.all import sniff, TCP, UDP, ICMP

from features.feature_utils import (
    compute_basic_features,
    fft_features,
    autocorr_features,
    entropy_features
)

# ---------------- CONFIG ----------------
MODEL_PATH = "models/rf_detector.joblib"
ALERT_LOG = "live/alerts.csv"

WINDOW_SIZE = 40
RISK_THRESHOLD = 60
BLOCK_THRESHOLD = 70

buffers = defaultdict(list)
blocked_ips = set()

# ---------------- LOAD MODEL ----------------
model_bundle = joblib.load(MODEL_PATH)
rf = model_bundle["model"]
scaler = model_bundle["scaler"]
RF_COLS = model_bundle["columns"]

# ---------------- PROTOCOL DETECTION ----------------
def detect_protocol(pkt):
    """
    Returns protocol label based on packet layers and ports
    """
    if pkt.haslayer(ICMP):
        return "ICMP"

    if pkt.haslayer(TCP):
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport

        if sport == 80 or dport == 80:
            return "HTTP"
        if sport == 443 or dport == 443:
            return "HTTPS"
        if sport == 443 or dport == 443:
            return "SSL"
        return "TCP"

    if pkt.haslayer(UDP):
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport

        if sport == 53 or dport == 53:
            return "DNS"
        return "UDP"

    return "OTHER"

# ---------------- AUTO BLOCK ----------------
# ---------------- BLOCK IP (Windows Firewall) ----------------
def block_ip(ip):
    """
    Block IP using Windows Defender Firewall.
    Requires admin PowerShell.
    """
    if ip in blocked_ips:
        return

    rule_name = f"CovertBlock_{ip}"

    cmd = [
        "powershell",
        "-Command",
        f"""
        if (-not (Get-NetFirewallRule -DisplayName '{rule_name}' -ErrorAction SilentlyContinue)) {{
            New-NetFirewallRule `
                -DisplayName '{rule_name}' `
                -Direction Inbound `
                -RemoteAddress {ip} `
                -Action Block
        }}
        """
    ]

    try:
        subprocess.run(cmd, check=True)
        blocked_ips.add(ip)
        print(f"[BLOCKED] {ip} blocked via Windows Firewall")
    except Exception as e:
        print(f"[WARN] Windows auto-block failed for {ip}: {e}")


# ---------------- LOG ALERT ----------------
def log_alert(row):
    exists = os.path.exists(ALERT_LOG)

    with open(ALERT_LOG, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "flow",
                "protocol",
                "final_risk",
                "ml_prob",
                "stat_score",
                "iforest_risk"
            ]
        )
        if not exists:
            writer.writeheader()
        writer.writerow(row)

# ---------------- PACKET HANDLER ----------------
def handle_packet(pkt):
    if not pkt.haslayer("IP"):
        return

    ip = pkt["IP"]
    proto_label = detect_protocol(pkt)

    flow = f"{ip.src}_{ip.dst}_{proto_label}"
    now = time.time()

    buffers[flow].append(now)

    if len(buffers[flow]) < WINDOW_SIZE:
        return

    times = np.array(buffers[flow][-WINDOW_SIZE:])
    ipds = np.diff(times)

    feats = {}
    feats.update(compute_basic_features(ipds))
    feats.update(fft_features(ipds))
    feats.update(autocorr_features(ipds))
    feats.update(entropy_features(ipds))

    X = pd.DataFrame([feats])
    X = X.reindex(columns=RF_COLS, fill_value=0.0)
    Xs = scaler.transform(X)

    ml_prob = rf.predict_proba(Xs)[0, 1]
    final_risk = ml_prob * 100

    stat_score = feats.get("ipd_entropy", 0) * 10
    iforest_risk = feats.get("ipd_std_norm", 0) * 100

    if final_risk >= RISK_THRESHOLD:
        print(f"[ALERT] {flow} | risk={final_risk:.2f}")

        log_alert({
            "timestamp": now,
            "flow": flow,
            "protocol": proto_label,
            "final_risk": round(final_risk, 2),
            "ml_prob": round(ml_prob * 100, 2),
            "stat_score": round(stat_score, 2),
            "iforest_risk": round(iforest_risk, 2)
        })

        if final_risk >= BLOCK_THRESHOLD:
            block_ip(ip.src)

# ---------------- MAIN ----------------
def run():
    print("[+] Real-time detection started")
    sniff(prn=handle_packet, store=False)

if __name__ == "__main__":
    run()
