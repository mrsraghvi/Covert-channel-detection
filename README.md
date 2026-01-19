---

# 🚨 Covert Timing Channel Detection System

**Machine Learning–Based Network IDS with Real-Time Detection & Dashboard**

---

## 📌 Project Overview

Covert timing channels are a stealthy communication technique where attackers encode information in the **timing between network packets**, bypassing traditional security controls.

This project implements a **full-stack Intrusion Detection System (IDS)** that:

* Detects **covert timing channels** using **Inter-Packet Delay (IPD) analysis**
* Uses **Machine Learning + Statistical tests**
* Supports **offline PCAP/CSV analysis**
* Supports **real-time live network traffic detection**
* Provides a **visual dashboard**
* Includes **severity levels and optional auto-blocking**

---

## 🎯 Key Features

✅ Covert channel simulation (ICMP / TCP timing)
✅ Packet capture (live + offline)
✅ IPD preprocessing & flow reconstruction
✅ Feature extraction (time, entropy, FFT, autocorrelation)
✅ ML detection (Random Forest + Isolation Forest)
✅ Statistical detection (KS test, entropy drift)
✅ **Real-time detection engine**
✅ **Live alerts with severity levels 🔴🟡🟢**
✅ **Streamlit dashboard**
✅ **Optional Windows firewall auto-block (admin only)**

---

## 🧠 Detection Architecture

```
Sender (Covert Traffic)
        ↓
Packet Capture (Live / CSV)
        ↓
Flow Reconstruction
        ↓
IPD Feature Extraction
        ↓
ML + Statistical Models
        ↓
Risk Fusion Engine
        ↓
Real-Time Alerts + Dashboard
```

---

## 📁 Project Structure

```
covert-channel-detector/
├── sender/                  # Covert channel traffic generator
├── capture/                 # Live & offline packet capture
├── preprocess/              # Flow parsing & IPD cleaning
├── features/                # Feature extraction
├── models/                  # ML models (RF, Isolation Forest)
├── stats/                   # Statistical tests
├── fusion/                  # Risk fusion engine
├── live/                    # Real-time detector & logger
├── dashboard/               # Streamlit dashboard
├── results/                 # ROC curves & plots
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation Guide (Windows – Recommended)

### 1️⃣ Install Miniconda (Recommended)

Download: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

---

### 2️⃣ Create Conda Environment

```bash
conda create -n covert python=3.10 -y
conda activate covert
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> If Scapy fails on Windows, run **Terminal as Administrator**

---

### 4️⃣ Verify Installation

```bash
python -c "import scapy, pandas, sklearn, streamlit; print('OK')"
```

---

## 🚀 How to Run the Project

---

## 🔹 Phase 1 — Covert Traffic Generation

### ICMP Covert Channel

```bash
python sender/sender_icmp.py 127.0.0.1 10101010 --repeat 10
```

---

## 🔹 Phase 2 — Packet Capture

### Live Capture

```bash
python capture/capture_live.py
```

### From CSV

```bash
python capture/capture_from_csv.py sender_output/<file>.csv
```

---

## 🔹 Phase 3 — Preprocessing & Feature Extraction

```bash
python preprocess/flow_splitter.py capture/capture_xxx.csv
```

```bash
python features/feature_extractor.py \
preprocessed/flows/normal.csv \
preprocessed/flows/covert.csv \
--window 50 --step 25
```

---

## 🔹 Phase 4 — Train Models

```bash
python models/train_model.py features/features_xxx.json
```

```bash
python models/iforest_detect.py features/features_xxx.json
```

---

## 🔹 Phase 5 — Risk Fusion

```bash
python fusion/risk_engine.py \
--features features/features_xxx.json \
--stats stats_output/stat_features_xxx.json \
--iforest models/iforest_scores.csv
```

---

## 🔹 Phase 6 — Real-Time Detection 🔥

⚠️ **Run terminal as Administrator**

```bash
python -m live.realtime_detector
```

### Sample Output

```
[ALERT] 192.168.1.4_192.168.1.1_17 | risk=63.75
```

Severity Levels:

* 🟢 Normal (< 40)
* 🟡 Suspicious (40–60)
* 🔴 Malicious (> 60)

---

## 📊 Dashboard (Streamlit)

```bash
streamlit run dashboard/app.py
```

### Dashboard Features

* Live alerts table
* Severity color coding
* Protocol filtering (TCP / UDP / ICMP)
* Attack timeline replay
* Risk trend visualization

---

## 🛡️ Auto-Blocking (Windows)

> ⚠️ Requires **Administrator PowerShell**

Blocking is implemented using **Windows Firewall rules** (not iptables).

```powershell
New-NetFirewallRule `
  -DisplayName "CovertBlock_192.168.1.4" `
  -Direction Inbound `
  -RemoteAddress 192.168.1.4 `
  -Action Block
```

Remove rule:

```powershell
Remove-NetFirewallRule -DisplayName "CovertBlock_192.168.1.4"
```

---

## 📈 Output Files

* `live/alerts.csv` → Real-time alerts
* `fusion_output/final_risk_report.csv`
* `results/roc_*.png`

---

## 🧪 Supported Protocols

* ICMP
* TCP
* UDP
* HTTP / HTTPS (via TCP timing)
* SSL/TLS (timing-based)

---

## 📚 Use Cases

* Covert channel detection
* Network intrusion detection
* Malware research
* Cybersecurity academic projects
* SOC monitoring demo

---

## ⚠️ Disclaimer

This project is **strictly for educational and research purposes**.
Do **NOT** use it on networks you do not own or have permission to test.

---

## 👨‍💻 Author

**Mr. Sraghvi**
Cybersecurity & Machine Learning Enthusiast
📧 **[mr.sraghvi@gmail.com](mailto:mr.sraghvi@gmail.com)**

---

## ⭐ If you like this project

Give it a **star ⭐ on GitHub** and feel free to fork!

---
