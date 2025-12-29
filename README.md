# 🕵️‍♂️ Covert Timing Channel Detection using Inter-Packet Delays

This project detects **covert timing channels** in network traffic by analyzing **inter-packet delay (IPD)** patterns using statistical features and machine learning.
It also includes a **SolarWinds-style interactive dashboard** for traffic visualization and analysis.

---

## 📌 Project Features

* Synthetic **covert timing channel generator**
* Packet capture normalization
* Flow-level preprocessing
* IPD-based feature extraction
* Machine Learning detection (Random Forest)
* Robustness testing with synthetic jitter
* ROC & AUC evaluation
* **SolarWinds-like traffic dashboard (Streamlit + Plotly)**

---

## 📁 Project Structure

```text
covert-channel-detector/
│
├── sender/                 # Covert traffic generation
│   └── sender_simulator.py
│
├── capture/                # Capture normalization
│   └── capture_from_csv.py
│
├── preprocess/             # Flow splitting & IPD cleaning
│   ├── parse_pcap.py
│   └── ipd_cleaning.py
│
├── preprocessed/
│   └── flows/              # Per-flow CSVs
│
├── features/               # Feature extraction
│   ├── feature_extractor.py
│   └── feature_utils.py
│
├── models/                 # Training & evaluation
│   ├── train_model.py
│   ├── eval_cv_save.py
│   └── feature_importance.py
│
├── dashboard/              # Visualization
│   └── app_v2.py
│
├── tools/                  # Noise & experiment scripts
│   ├── make_noisy_flow.py
│   └── sweep_jitter.py
│
├── results/                # ROC curves & summaries
├── requirements.txt
└── README.md
```

---

## 🧰 System Requirements

* **OS:** Windows / Linux / macOS
* **Python:** 3.9 – 3.11
* **Conda** (recommended) or `venv`
* Minimum **8 GB RAM** recommended

---

## 🚀 Installation Guide (Recommended: Conda)

### 1️⃣ Install Miniconda / Anaconda

Download from:
[https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/covert-channel-detector.git
cd covert-channel-detector
```

---

### 3️⃣ Create & Activate Conda Environment

```bash
conda create -n covert python=3.10 -y
conda activate covert
```

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If Plotly is missing:

```bash
pip install plotly
```

---

### 5️⃣ Verify Installation

```bash
python -c "import pandas, numpy, sklearn, matplotlib, streamlit, plotly; print('SETUP_OK')"
```

Expected output:

```text
SETUP_OK
```

---

## ▶️ How to Run the Project

### 🔹 Step 1: Generate Synthetic Traffic

```bash
python sender/sender_simulator.py
```

Output:

```text
sender_output/YYYYMMDD_packets.csv
```

---

### 🔹 Step 2: Normalize Capture

```bash
python capture/capture_from_csv.py sender_output/YYYYMMDD_packets.csv
```

---

### 🔹 Step 3: Flow Splitting

Automatically creates:

```text
preprocessed/flows/
```

---

### 🔹 Step 4: Feature Extraction

```bash
python features/feature_extractor.py preprocessed/flows/*.csv --window 50 --step 25
```

Output:

```text
features/features_YYYYMMDD.json
```

---

### 🔹 Step 5: Train Detection Model

```bash
python models/train_model.py features/features_YYYYMMDD.json
```

Model saved as:

```text
models/rf_detector.joblib
```

---

### 🔹 Step 6: Evaluate Model (CV + ROC)

```bash
python models/eval_cv_save.py features/features_YYYYMMDD.json
```

ROC saved to:

```text
results/roc_features_YYYYMMDD.png
```

---

## 📊 Run the Dashboard (SolarWinds-Style)

```bash
streamlit run dashboard/app_v2.py
```

Then open browser:

```text
http://localhost:8501
```

### Dashboard Features

* Stacked traffic area charts
* Mini scrubber timeline
* Top conversations & endpoints
* Interactive filters (time, bin size, flows)

---

## 🔬 Robustness Testing (Noise Injection)

### Add jitter to covert flow

```bash
python tools/make_noisy_flow.py preprocessed/flows/10.0.0.3_10.0.0.4_ICMP.csv --jitter 0.05
```

### Re-extract features and retrain

```bash
python features/feature_extractor.py preprocessed/flows/*noisy*.csv
python models/train_model.py features/features_*.json
```

---

## 📈 Automated Jitter Sweep (Optional)

```bash
python tools/sweep_jitter.py
```

Generates:

* Multiple ROC curves
* `results/sweep_summary.csv`

---

## 🧪 Technologies Used

* Python
* Scapy
* Pandas / NumPy / SciPy
* Scikit-learn
* Streamlit
* Plotly
* Matplotlib

---

## ⚠️ Disclaimer

This project is **for educational and research purposes only**.
It does **not** perform real attacks and does **not** capture live traffic without consent.

---

## 📌 Future Enhancements

* FFT & spectral IPD features
* Real PCAP ingestion
* Online detection mode
* Deep learning classifiers
* Alerting system

---

## 👨‍💻 Author

Developed as a **Cybersecurity / Network Security Project**
Focused on **Covert Channel Detection**

---

### ✅ Your markdownlint issues are now fixed

If you still see warnings, tell me:

* the rule ID
* the line number

and I’ll fix those too 💪
