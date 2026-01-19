# stats/stat_tests.py
"""
Statistical tests for covert timing channel detection.
Purely distribution-based and explainable.
"""

import numpy as np
from scipy.stats import ks_2samp, anderson
from scipy.spatial.distance import jensenshannon
# -------------------------------------------------
# Real-time statistical score (Phase 2 support)
# -------------------------------------------------
import numpy as np
from scipy.stats import ks_2samp

def compute_stat_scores(ipds, baseline_ipds=None):
    """
    Compute a single statistical risk score from IPDs.
    Used for real-time detection.
    """

    ipds = np.asarray(ipds)

    if len(ipds) < 10:
        return 0.0

    # Use self-baseline if no reference provided
    if baseline_ipds is None:
        baseline_ipds = ipds[: len(ipds)//2]

    baseline_ipds = np.asarray(baseline_ipds)

    # Kolmogorov–Smirnov test
    ks_stat, _ = ks_2samp(ipds, baseline_ipds)

    # Normalize to percentage
    stat_risk = min(ks_stat * 100, 100.0)

    return float(stat_risk)

# -------------------------------------------------
# Utility
# -------------------------------------------------
def normalize_hist(x, bins=20):
    hist, _ = np.histogram(x, bins=bins, density=True)
    hist = hist + 1e-9
    return hist / np.sum(hist)

# -------------------------------------------------
# Statistical Tests
# -------------------------------------------------
def ks_test(ipd_window, baseline_ipd):
    stat, pval = ks_2samp(ipd_window, baseline_ipd)
    return float(stat), float(pval)

def ad_test(ipd_window):
    result = anderson(ipd_window, dist="expon")
    return float(result.statistic)

def js_divergence(ipd_window, baseline_ipd):
    p = normalize_hist(ipd_window)
    q = normalize_hist(baseline_ipd)
    return float(jensenshannon(p, q))

# -------------------------------------------------
# Combined Suspicion Score
# -------------------------------------------------
def suspicion_score(ks_stat, ks_p, ad_stat, jsd):
    """
    Convert statistical evidence into a 0–100 risk score
    """
    score = 0.0

    # KS test
    if ks_p < 0.05:
        score += min(ks_stat * 40, 40)

    # Anderson–Darling
    score += min(ad_stat * 5, 25)

    # Jensen–Shannon divergence
    score += min(jsd * 100, 35)

    return min(100.0, score)
