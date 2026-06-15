"""Vectorized portfolio backtest engine.

Convention (important, to avoid look-ahead bias):
    weights.loc[t]  = the position HELD over period t, i.e. it earns returns.loc[t].
The strategy is responsible for lagging its signal so that weights.loc[t] uses
only information available *before* period t. The engine does not shift for you.

This in-house engine handles any cross-sectional / time-series weight matrix and
is the default for the program. An event-driven library (vectorbt) is reserved
for projects that need intra-period fills / order books.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def backtest(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    cost_bps: float = 0.0,
) -> pd.DataFrame:
    """Run a weight matrix against a returns matrix.

    Parameters
    ----------
    weights   : target position per asset per period (already lagged).
    returns   : simple returns per asset per period.
    cost_bps  : round-trip transaction cost in basis points, charged on turnover.

    Returns
    -------
    DataFrame with columns: gross, net, turnover, equity_gross, equity_net.
    """
    w = weights.reindex(returns.index).reindex(columns=returns.columns).fillna(0.0)
    r = returns.fillna(0.0)

    gross = (w * r).sum(axis=1)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0)
    costs = turnover * (cost_bps / 1e4)
    net = gross - costs

    out = pd.DataFrame({"gross": gross, "net": net, "turnover": turnover})
    out["equity_gross"] = (1.0 + out["gross"]).cumprod()
    out["equity_net"] = (1.0 + out["net"]).cumprod()
    return out
