
````
# 🚨 Covert Timing Channel Detection System

**Machine Learning–Based Network Intrusion Detection System (IDS)**  
Real-time detection of covert timing channels using statistical analysis, machine learning, and live traffic monitoring.

---

## 📌 Project Overview

Covert timing channels hide information by manipulating packet timing rather than payload content.  
This project detects such attacks using:

- Inter-Packet Delay (IPD) analysis
- Statistical hypothesis testing
- Machine learning classifiers
- Real-time packet inspection
- Interactive monitoring dashboard

The system behaves like a **lightweight Network IDS**, inspired by tools such as Zeek and Suricata.

---

## 🧠 Key Features

- Live packet capture using Scapy
- IPD-based feature extraction
- Random Forest (supervised detection)
- Isolation Forest (anomaly detection)
- Risk score fusion engine
- Real-time alerts
- Severity levels (🟢 Low, 🟡 Medium, 🔴 High)
- Interactive Streamlit dashboard
- Attack timeline replay
- Continuous alert logging
- Offline and online analysis modes

---

## 🏗 Project Architecture

```text
covert-channel-detector/
├── sender/        # Covert traffic generators (ICMP/TCP)
├── capture/       # Packet capture & PCAP handling
├── preprocess/    # Flow parsing & IPD cleaning
├── features/      # Feature extraction modules
├── models/        # ML models & inference
├── fusion/        # Risk fusion engine
├── live/          # Real-time detector & logger
├── dashboard/     # Streamlit dashboard
├── tools/         # Noise injection & experiments
├── results/       # ROC curves & outputs
└── README.md
````

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/covert-channel-detector.git
cd covert-channel-detector
```

---

### 2️⃣ Create Conda Environment (Recommended)

```bash
conda create -n covert python=3.10 -y
conda activate covert
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> **Windows users:** Install **Npcap** with WinPcap compatibility enabled.

---

## ▶️ Running the Project

### 🔹 Option 1 — Full System (Recommended)

```bash
run_all.bat
```

This starts:

* Live packet logger
* Real-time ML detector
* Streamlit dashboard

---

### 🔹 Option 2 — Manual Execution

#### Start live packet logger

```bash
python live/live_logger.py
```

#### Start real-time detector

```bash
python -m live.realtime_detector
```

#### Start dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📊 Dashboard Capabilities

* Live alerts table (select number of visible alerts)
* Severity-based coloring
* Protocol filters (ICMP, UDP, TCP)
* Risk trend visualization
* Attack replay timeline slider
* Top suspicious flows
* Manual IP block/unblock controls

Dashboard URL:

```text
http://localhost:8501
```

---

## 🧪 Offline Experiment Pipeline

```bash
python sender/sender_icmp.py 127.0.0.1 10101010 --repeat 5
python capture/capture_from_csv.py sender_output/<file>.csv
python preprocess/flow_splitter.py capture/<file>.csv
python features/feature_extractor.py preprocessed/flows/*.csv
python models/train_model.py features/features_*.json
```

---

## 📈 Results Summary

* High detection accuracy on synthetic covert traffic
* ROC-AUC close to 1.0 in controlled experiments
* Robust detection under jitter/noise
* Successful real-time alerting during live traffic

---

## 🛡 Ethics & Legal Notice

This project is intended **only for educational and research purposes**.
Do **not** deploy on networks without explicit authorization.

---

## 🧾 Technologies Used

* Python
* Scapy
* Pandas / NumPy
* Scikit-learn
* Streamlit
* Plotly
* Matplotlib

---

## 👤 Author

* **Name:** Mr. Sraghvi
* **Email:** [mr.sraghvi@gmail.com](mailto:mr.sraghvi@gmail.com)
* **Domain:** Cybersecurity, Network Security, Machine Learning

---

## ⭐ Future Enhancements

* Docker-based deployment
* SIEM integration
* Deep learning models (LSTM/GRU)
* Distributed sensor nodes
* Native Windows firewall auto-blocking
* Threat intelligence feeds

---

## 📜 License

MIT License — Free for academic and research use.
