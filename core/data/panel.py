"""Free firm-level characteristic panel (price/volume features only).

Builds the kind of stock x month x characteristic panel that ML asset-pricing
papers (GKX, Deep-Learning-APT, AlphaPortfolio) consume — but entirely from free
yfinance OHLCV, so no WRDS/CRSP needed. Fundamentals (value/profitability) from
SEC EDGAR are a documented later upgrade.

All characteristics at month t use only data through the end of month t; the
target is the return of month t+1 (no look-ahead).

    build_panel(universe, start) -> long DataFrame indexed by (date, ticker)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .prices import get_ohlc

CHARS = ["mom12_1", "mom6_1", "ltr", "strev", "vol12", "maxret", "amihud", "dvol", "beta"]


def _stock_features(df: pd.DataFrame, mkt_m: pd.Series | None) -> pd.DataFrame:
    c = df["Close"]
    dret = c.pct_change()
    dvol_daily = (c * df["Volume"]).replace(0, np.nan)

    cm = c.resample("ME").last()
    rm = cm.pct_change()
    feats = pd.DataFrame(index=cm.index)
    feats["mom12_1"] = cm.shift(1) / cm.shift(12) - 1           # 12-1 momentum
    feats["mom6_1"] = cm.shift(1) / cm.shift(6) - 1             # 6-1 momentum
    feats["ltr"] = cm.shift(13) / cm.shift(36) - 1             # long-term reversal
    feats["strev"] = rm                                         # short-term reversal
    feats["vol12"] = rm.rolling(12).std() * np.sqrt(12)        # volatility
    feats["maxret"] = dret.resample("ME").max()                # lottery / max daily
    feats["amihud"] = (dret.abs() / dvol_daily).resample("ME").mean()  # illiquidity
    feats["dvol"] = np.log(dvol_daily.resample("ME").mean())   # size/liquidity proxy
    if mkt_m is not None:
        cov = rm.rolling(24).cov(mkt_m)
        feats["beta"] = cov / mkt_m.rolling(24).var()
    else:
        feats["beta"] = np.nan
    feats["ret_fwd"] = rm.shift(-1)                             # target: next month
    return feats


def build_panel(universe: list[str], start: str = "2005-01-01") -> pd.DataFrame:
    # market proxy = equal-weight monthly return of the universe
    closes = {}
    for tk in universe:
        try:
            closes[tk] = get_ohlc(tk, start=start)["Close"]
        except Exception:
            continue
    cm = pd.DataFrame(closes).resample("ME").last()
    mkt_m = cm.pct_change().mean(axis=1)

    frames = []
    for tk in closes:
        df = get_ohlc(tk, start=start)
        f = _stock_features(df, mkt_m)
        f["ticker"] = tk
        frames.append(f.reset_index().rename(columns={"index": "date", "Date": "date"}))
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.rename(columns={panel.columns[0]: "date"}) if "date" not in panel else panel
    panel = panel.set_index(["date", "ticker"]).sort_index()
    return panel.replace([np.inf, -np.inf], np.nan)


def standardize_cross_section(panel: pd.DataFrame, cols=CHARS) -> pd.DataFrame:
    """Rank-normalise each characteristic to [-1, 1] within each month (GKX style)."""
    out = panel.copy()
    g = out.groupby(level="date")
    for col in cols:
        out[col] = g[col].transform(lambda s: 2 * s.rank(pct=True) - 1)
    return out
