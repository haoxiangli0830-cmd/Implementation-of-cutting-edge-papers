"""Performance metrics + the overfitting-rigor layer.

Standard metrics (Sharpe, Sortino, max drawdown, CAGR) PLUS:
  - Probabilistic Sharpe Ratio (PSR)        Bailey & Lopez de Prado (2012)
  - Deflated Sharpe Ratio (DSR)             Bailey & Lopez de Prado (2014)

The deflated Sharpe is the headline honesty check: it asks "given that we tried
N strategy variants, is this Sharpe still significant, accounting for non-normal
returns?" A naive Sharpe that looks great can have DSR ~ 0.5 (i.e. no better than
a coin flip) once multiple testing is accounted for.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

EULER_MASCHERONI = 0.5772156649015329


def _ann(periods_per_year: int) -> float:
    return float(periods_per_year)


def sharpe(returns: pd.Series, periods_per_year: int = 12, rf: float = 0.0) -> float:
    r = returns.dropna() - rf / periods_per_year
    if r.std(ddof=1) == 0 or len(r) < 2:
        return float("nan")
    return float(r.mean() / r.std(ddof=1) * np.sqrt(periods_per_year))


def sortino(returns: pd.Series, periods_per_year: int = 12, rf: float = 0.0) -> float:
    r = returns.dropna() - rf / periods_per_year
    downside = r[r < 0]
    dd = np.sqrt((downside ** 2).mean()) if len(downside) else np.nan
    if not dd or np.isnan(dd):
        return float("nan")
    return float(r.mean() / dd * np.sqrt(periods_per_year))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1 + returns.fillna(0)).cumprod()
    peak = equity.cummax()
    return float((equity / peak - 1).min())


def cagr(returns: pd.Series, periods_per_year: int = 12) -> float:
    r = returns.dropna()
    if len(r) == 0:
        return float("nan")
    total = (1 + r).prod()
    years = len(r) / periods_per_year
    return float(total ** (1 / years) - 1) if years > 0 and total > 0 else float("nan")


def probabilistic_sharpe_ratio(
    returns: pd.Series, sr_benchmark: float = 0.0, periods_per_year: int = 12
) -> float:
    """P(true Sharpe > benchmark), adjusting for sample length, skew and kurtosis.

    sr_benchmark is given ANNUALISED; converted internally to per-period.
    """
    r = returns.dropna()
    n = len(r)
    if n < 3:
        return float("nan")
    sr = sharpe(r, periods_per_year) / np.sqrt(periods_per_year)        # per-period
    sr0 = sr_benchmark / np.sqrt(periods_per_year)
    skew = float(stats.skew(r))
    kurt = float(stats.kurtosis(r, fisher=False))                       # non-excess
    denom = np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    if denom == 0:
        return float("nan")
    z = (sr - sr0) * np.sqrt(n - 1) / denom
    return float(stats.norm.cdf(z))


def _expected_max_sharpe(sr_trials_std: float, n_trials: int) -> float:
    """Expected maximum of N independent trial Sharpes (per-period units).

    From the false-strategy theorem (Bailey & Lopez de Prado 2014).
    """
    if n_trials < 2 or sr_trials_std <= 0:
        return 0.0
    g = EULER_MASCHERONI
    z1 = stats.norm.ppf(1 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return sr_trials_std * ((1 - g) * z1 + g * z2)


def deflated_sharpe_ratio(
    returns: pd.Series,
    n_trials: int,
    sr_trials_std: float,
    periods_per_year: int = 12,
) -> float:
    """Deflated Sharpe Ratio: PSR against the expected-max-Sharpe of N trials.

    Parameters
    ----------
    n_trials       : how many strategy variants were tried (e.g. parameter sweep).
    sr_trials_std  : std-dev of the ANNUALISED Sharpes across those trials.

    Returns DSR in [0,1]; > 0.95 is the usual "survives multiple testing" bar.
    """
    sr0_perp = _expected_max_sharpe(sr_trials_std / np.sqrt(periods_per_year), n_trials)
    sr0_ann = sr0_perp * np.sqrt(periods_per_year)
    return probabilistic_sharpe_ratio(returns, sr_benchmark=sr0_ann,
                                      periods_per_year=periods_per_year)


def performance_summary(returns: pd.Series, periods_per_year: int = 12) -> dict:
    r = returns.dropna()
    return {
        "n_periods": int(len(r)),
        "cagr": cagr(r, periods_per_year),
        "ann_vol": float(r.std(ddof=1) * np.sqrt(periods_per_year)),
        "sharpe": sharpe(r, periods_per_year),
        "sortino": sortino(r, periods_per_year),
        "max_drawdown": max_drawdown(r),
        "skew": float(stats.skew(r)) if len(r) > 2 else float("nan"),
        "psr_vs_0": probabilistic_sharpe_ratio(r, 0.0, periods_per_year),
    }
