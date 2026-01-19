# features/feature_utils.py
"""
Feature utilities for covert timing channel detection
(Shared by offline + real-time modules)
"""

import numpy as np
from scipy.stats import entropy
from scipy.signal import correlate
from scipy.fft import rfft

# -------------------------------------------------
# BASIC FEATURES (Real-time safe)
# -------------------------------------------------
def compute_basic_features(ipds):
    ipds = np.asarray(ipds)

    if len(ipds) < 2:
        return {
            "ipd_mean": 0.0,
            "ipd_std": 0.0,
            "ipd_min": 0.0,
            "ipd_max": 0.0,
            "ipd_entropy": 0.0,
            "ipd_std_norm": 0.0,
        }

    hist, _ = np.histogram(ipds, bins=10, density=True)
    hist += 1e-9

    return {
        "ipd_mean": float(np.mean(ipds)),
        "ipd_std": float(np.std(ipds)),
        "ipd_min": float(np.min(ipds)),
        "ipd_max": float(np.max(ipds)),
        "ipd_entropy": float(entropy(hist)),
        "ipd_std_norm": float(np.std(ipds) / (np.mean(ipds) + 1e-9)),
    }

# -------------------------------------------------
# FFT FEATURES
# -------------------------------------------------
def fft_features(ipd):
    ipd = np.asarray(ipd)
    if len(ipd) < 4:
        return {
            "fft_dom_freq": 0.0,
            "fft_energy_ratio": 0.0,
            "fft_spectral_entropy": 0.0
        }

    x = ipd - np.mean(ipd)
    fft_vals = np.abs(rfft(x)) ** 2

    if np.sum(fft_vals) == 0:
        return {
            "fft_dom_freq": 0.0,
            "fft_energy_ratio": 0.0,
            "fft_spectral_entropy": 0.0
        }

    dom_freq = np.argmax(fft_vals[1:]) + 1
    low_energy = np.sum(fft_vals[:len(fft_vals)//4])
    high_energy = np.sum(fft_vals[len(fft_vals)//4:])

    return {
        "fft_dom_freq": float(dom_freq),
        "fft_energy_ratio": float(low_energy / (high_energy + 1e-9)),
        "fft_spectral_entropy": float(entropy(fft_vals / np.sum(fft_vals)))
    }

# -------------------------------------------------
# AUTOCORRELATION FEATURES
# -------------------------------------------------
def autocorr_features(ipd, max_lag=10):
    ipd = np.asarray(ipd)
    if len(ipd) < max_lag + 2:
        return {
            "ac_max": 0.0,
            "ac_lag": 0.0,
            "ac_mean": 0.0
        }

    x = ipd - np.mean(ipd)
    corr = correlate(x, x, mode="full")
    corr = corr[corr.size // 2:]
    corr /= np.max(corr) if np.max(corr) != 0 else 1

    ac_vals = corr[1:max_lag + 1]

    return {
        "ac_max": float(np.max(ac_vals)),
        "ac_lag": float(np.argmax(ac_vals) + 1),
        "ac_mean": float(np.mean(ac_vals))
    }

# -------------------------------------------------
# ENTROPY WRAPPER (compat)
# -------------------------------------------------
def entropy_features(ipd):
    ipd = np.asarray(ipd)
    if len(ipd) < 5:
        return {
            "ipd_entropy": 0.0,
            "ipd_std_norm": 0.0
        }

    hist, _ = np.histogram(ipd, bins=10, density=True)
    hist += 1e-9

    return {
        "ipd_entropy": float(entropy(hist)),
        "ipd_std_norm": float(np.std(ipd) / (np.mean(ipd) + 1e-9))
    }
