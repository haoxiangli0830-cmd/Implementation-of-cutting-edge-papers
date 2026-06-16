"""Value-at-Risk, Expected Shortfall, and Basel backtesting.

Conventions: returns are simple P&L returns (e.g. -0.03 = a 3% loss). VaR and ES
are reported as POSITIVE loss magnitudes at confidence `alpha` (e.g. 0.99). A VaR
"exception" (breach) is a day where the realised loss exceeds the VaR estimate.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


# --- VaR / ES estimators -----------------------------------------------------
def historical_var(returns, alpha: float = 0.99) -> float:
    return float(-np.percentile(returns, (1 - alpha) * 100))


def historical_es(returns, alpha: float = 0.99) -> float:
    var = historical_var(returns, alpha)
    tail = np.asarray(returns)[np.asarray(returns) <= -var]
    return float(-tail.mean()) if len(tail) else var


def parametric_var(returns, alpha: float = 0.99) -> float:
    mu, sigma = np.mean(returns), np.std(returns, ddof=1)
    return float(-(mu + stats.norm.ppf(1 - alpha) * sigma))


def parametric_es(returns, alpha: float = 0.99) -> float:
    mu, sigma = np.mean(returns), np.std(returns, ddof=1)
    z = stats.norm.ppf(1 - alpha)
    return float(-(mu - sigma * stats.norm.pdf(z) / (1 - alpha)))


def monte_carlo_var(returns, alpha: float = 0.99, n: int = 100_000, seed: int = 0) -> float:
    mu, sigma = np.mean(returns), np.std(returns, ddof=1)
    sim = np.random.default_rng(seed).normal(mu, sigma, n)
    return float(-np.percentile(sim, (1 - alpha) * 100))


# --- Basel backtesting --------------------------------------------------------
def kupiec_pof(exceptions: int, n: int, alpha: float = 0.99):
    """Kupiec proportion-of-failures (unconditional coverage) LR test -> (LR, p)."""
    p = 1 - alpha
    x = exceptions
    if x == 0:
        lr = -2 * n * np.log(1 - p)
    else:
        pi = x / n
        lr = -2 * ((n - x) * np.log((1 - p) / (1 - pi)) + x * np.log(p / pi))
    return float(lr), float(1 - stats.chi2.cdf(lr, 1))


def christoffersen_independence(breaches):
    """Christoffersen test that breaches are independent (no clustering) -> (LR, p)."""
    b = np.asarray(breaches).astype(int)
    n00 = n01 = n10 = n11 = 0
    for prev, cur in zip(b[:-1], b[1:]):
        if prev == 0 and cur == 0: n00 += 1
        elif prev == 0 and cur == 1: n01 += 1
        elif prev == 1 and cur == 0: n10 += 1
        else: n11 += 1
    pi01 = n01 / (n00 + n01) if (n00 + n01) else 0
    pi11 = n11 / (n10 + n11) if (n10 + n11) else 0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    if pi in (0, 1) or pi01 in (0, 1) or pi11 in (0, 1):
        return 0.0, 1.0
    num = (1 - pi) ** (n00 + n10) * pi ** (n01 + n11)
    den = (1 - pi01) ** n00 * pi01 ** n01 * (1 - pi11) ** n10 * pi11 ** n11
    lr = -2 * np.log(num / den)
    return float(lr), float(1 - stats.chi2.cdf(lr, 1))


def basel_traffic_light(exceptions: int, window: int = 250) -> str:
    """Basel traffic-light zone for a 99% 1-day VaR over `window` days (default 250)."""
    if window != 250:
        # scale the 250-day thresholds (5 / 10) proportionally
        green = round(4 * window / 250); yellow = round(9 * window / 250)
    else:
        green, yellow = 4, 9
    if exceptions <= green:
        return "GREEN (model adequate)"
    if exceptions <= yellow:
        return "YELLOW (raise capital multiplier)"
    return "RED (model rejected)"
