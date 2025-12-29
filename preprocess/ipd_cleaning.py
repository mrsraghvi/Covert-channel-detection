# preprocess/ipd_cleaning.py
"""
Functions to clean IPD timeseries: remove outliers, rescale timestamps, and optionally apply jitter model.
"""
import numpy as np
import pandas as pd

def compute_ipd(df, ts_col="ts"):
    df = df.sort_values(ts_col).reset_index(drop=True)
    df["ipd"] = df[ts_col].diff().fillna(0.0)
    return df

def remove_outlier_ipds(df, ipd_col="ipd", z_thresh=5.0):
    arr = df[ipd_col].values
    mean = np.mean(arr)
    std = np.std(arr) if np.std(arr) > 0 else 1.0
    z = np.abs((arr - mean) / std)
    mask = z < z_thresh
    return df[mask].reset_index(drop=True)

def rescale_timestamps(df, ts_col="ts", start_at_zero=True):
    df = df.copy()
    if start_at_zero:
        df[ts_col] = df[ts_col] - df[ts_col].min()
    return df

def apply_synthetic_jitter(df, ipd_col="ipd", jitter_std=0.002):
    df = df.copy()
    jitter = np.random.normal(0, jitter_std, size=len(df))
    df[ipd_col] = np.maximum(1e-9, df[ipd_col] + jitter)
    return df
