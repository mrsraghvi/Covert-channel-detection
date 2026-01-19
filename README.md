---

# 🛡️ Covert Channel Detector (Timing-Based IDS)

A **machine learning–powered Intrusion Detection System (IDS)** to detect **covert timing channels** in network traffic using **Inter-Packet Delay (IPD) analysis**, **statistical tests**, and **real-time monitoring**.

This project supports:

* Offline analysis from PCAP / CSV
* ML-based detection (Random Forest + Isolation Forest)
* Statistical hypothesis testing
* **Real-time live traffic detection**
* **Automatic IP blocking (Windows Firewall / Linux iptables)**
* Interactive **Streamlit dashboard**

---

## 📌 Features

* ✅ Covert timing channel detection (ICMP / TCP / UDP)
* ✅ Feature extraction: IPD, entropy, FFT, autocorrelation
* ✅ ML models: Random Forest, Isolation Forest
* ✅ Risk fusion engine (ML + stats + anomaly score)
* ✅ Real-time packet sniffing using Scapy
* ✅ Auto-blocking of malicious IPs
* ✅ Streamlit dashboard with alerts & timeline
* ✅ Designed for **academic + industry demo**

---

## 🧱 Project Structure

```
covert-channel-detector/
│
├── capture/                # Packet capture (CSV / PCAP)
├── preprocess/             # Flow parsing & cleaning
├── features/               # Feature extraction logic
├── models/                 # Trained ML models
├── stats/                  # Statistical tests (KS, entropy)
├── fusion/                 # Risk fusion engine
├── sender/                 # Covert channel traffic generator
├── live/                   # Real-time detection & logging
├── dashboard/              # Streamlit dashboard
├── results/                # ROC curves & plots
├── requirements.txt
└── README.md
```

---

## ⚙️ System Requirements

### OS

* Windows 10 / 11 **(Admin access required for firewall rules)**
* Linux (optional, iptables supported)

### Software

* Python **3.9 – 3.11**
* Miniconda / Anaconda (recommended)
* PowerShell (Windows)

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/covert-channel-detector.git
cd covert-channel-detector
```

---

### 2️⃣ Create virtual environment

#### Using Conda (Recommended)

```bash
conda create -n covert python=3.10 -y
conda activate covert
```

#### OR using venv

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📄 Requirements (`requirements.txt`)

```txt
scapy
pandas
numpy
scipy
scikit-learn
joblib
matplotlib
streamlit
plotly
```

---

## 🚀 How to Run the Project

---

## 🔹 Phase 1 — Generate Covert Traffic (Test Data)

```bash
python sender/sender_icmp.py 127.0.0.1 10101010 --repeat 10
```

✔️ Sends ICMP packets using timing modulation

---

## 🔹 Phase 2 — Feature Extraction

```bash
python features/feature_extractor.py \
preprocessed/flows/10.0.0.1_10.0.0.2_TCP.csv \
preprocessed/flows/10.0.0.3_10.0.0.4_ICMP.csv \
--window 50 --step 25
```

✔️ Outputs JSON feature file

---

## 🔹 Phase 3 — Train Detection Model

```bash
python models/train_model.py features/features_YYYYMMDD_HHMMSS.json
```

✔️ Saves trained model in `models/`

---

## 🔹 Phase 4 — Real-Time Detection (LIVE IDS)

⚠️ **Run terminal as Administrator**

```bash
python -m live.realtime_detector
```

You will see output like:

```text
[ALERT] 192.168.1.4_192.168.1.1_17 | risk=72.67
[BLOCKED] 192.168.1.4 blocked via Windows Firewall
```

---

## 🔥 Auto-Blocking (Windows)

* Uses **Windows Defender Firewall**
* Automatically blocks IPs with high risk

### View blocked IPs (PowerShell Admin)

```powershell
Get-NetFirewallRule | Where-Object DisplayName -Like "CovertBlock*"
```

### Remove a block

```powershell
Remove-NetFirewallRule -DisplayName "CovertBlock_192.168.1.4"
```

---

## 📊 Dashboard (Alerts & Timeline)

```bash
streamlit run dashboard/app.py
```

Dashboard features:

* 🔴🟡🟢 Severity-colored alerts
* Protocol filters (TCP / UDP / ICMP)
* Attack timeline replay
* Risk trend graphs

---

## 🧪 Output Files

| File                    | Description          |
| ----------------------- | -------------------- |
| `alerts.csv`            | Real-time alert logs |
| `rf_detector.joblib`    | ML detection model   |
| `iforest_scores.csv`    | Anomaly scores       |
| `final_risk_report.csv` | Fused risk output    |

---

## 🎓 Academic Relevance

This project demonstrates:

* Network security & covert channels
* Time-series feature engineering
* Supervised + unsupervised ML
* IDS architecture
* Real-time systems design

Perfect for:

* Final year project
* Cybersecurity internships
* Research demos
* Resume / GitHub portfolio

---

## ⚠️ Disclaimer

This project is for **educational and defensive security research only**.
Do **NOT** deploy on networks without permission.


---

## 👨‍💻 Author

**Mr. Sraghvi**
Cybersecurity & Machine Learning Enthusiast
📧 **[mr.sraghvi@gmail.com](mailto:mr.sraghvi@gmail.com)**


---

## ⭐ If You Like This Project

Please ⭐ star the repository and share!

---
