# features/feature_utils.py
"""
Utility helpers for feature extraction.
"""
import numpy as np

def autocorr_lag1(arr):
    arr = np.array(arr)
    if len(arr) < 2:
        return 0.0
    a = arr[:-1] - arr[:-1].mean()
    b = arr[1:] - arr[1:].mean()
    denom = (a.std() * b.std())
    if denom == 0:
        return 0.0
    return float((a * b).mean() / denom)
