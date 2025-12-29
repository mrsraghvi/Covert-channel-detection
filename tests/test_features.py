# tests/test_features.py
"""
Basic pytest-based unit tests for feature extractor utilities.
Run: pytest -q
"""
import os
import pandas as pd
from features.feature_utils import autocorr_lag1
from features.feature_extractor import extract_from_flow_csv
import json
import tempfile

def test_autocorr_constant():
    arr = [1.0] * 5
    v = autocorr_lag1(arr)
    assert isinstance(v, float)
    assert abs(v) < 1e-6  # zero variance -> autocorr ~ 0

def test_extract_windows(tmp_path):
    # create a dummy flow csv
    csv_path = tmp_path / "flow.csv"
    df = pd.DataFrame({"ts": [0, 0.01, 0.02, 0.05, 0.2], "src":["a"]*5, "dst":["b"]*5, "sport":[0]*5, "dport":[0]*5, "proto":["ICMP"]*5, "length":[64]*5})
    df["ipd"] = df["ts"].diff().fillna(0)
    df.to_csv(csv_path, index=False)
    feats = extract_from_flow_csv(str(csv_path), window=3, step=2)
    assert isinstance(feats, list)
    assert len(feats) >= 1
