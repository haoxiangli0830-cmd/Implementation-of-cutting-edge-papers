# Report — rk-01: Market-risk VaR / ES + Basel backtesting

**This is the core deliverable of a bank market-risk desk**, and the result
reproduces both the standard practice *and* the well-known limitation that
motivates modern methods.

## The book
Equal-weight multi-asset ETF book (SPY, EFA, EEM, TLT, IEF, GLD, DBC, VNQ),
daily, 2007→present.

## Current 1-day risk (% of book)
| Method | VaR 99% (Basel) | ES 97.5% (FRTB) |
|---|---|---|
| Historical | **2.06%** | 1.93% |
| Parametric (normal) | 1.42% | 1.42% |
| Monte-Carlo (normal) | 1.43% | 1.93% |

**Lesson 1 — the normal model understates tail risk.** Historical VaR (2.06%) is
~45% higher than the normal-based estimates (1.42%), because real returns have
fatter tails and skew than a Gaussian. Reporting only parametric VaR would
systematically under-reserve capital.

## Backtest (99% historical VaR, 4,391 out-of-sample days)
| Check | Result | Verdict |
|---|---|---|
| Exceptions | 46 observed vs ~44 expected | right count |
| **Kupiec POF** (coverage) | LR 0.10, p = 0.75 | **PASS** |
| **Christoffersen** (independence) | LR 20.6, p = 0.000 | **FAIL — breaches cluster** |
| Basel traffic-light (last 250d, 4 exc) | **GREEN** | model adequate |

See `results/var_backtest.png` (red dots = breaches — note how they bunch in 2008,
2020).

## The key finding (and the bridge to the rest of the track)
The model has the **right number** of breaches (Kupiec passes) but they are **not
independent** — they cluster in volatile periods (Christoffersen fails, p≈0). A
250-day historical VaR reacts slowly to a volatility spike, so during a crisis it
breaches several days in a row. This is the canonical weakness of simple VaR and
the reason the industry moved toward:
- **EWMA / GARCH volatility-scaled VaR** (reacts faster),
- **Expected Shortfall (FRTB)** (captures tail size, not just a threshold),
- and ML approaches (`rk-f3` quantile-regression nets) — later in this track.

## Methods & practices demonstrated
✔ Three VaR engines · ✔ ES at the FRTB 97.5% level · ✔ rolling OOS backtest ·
✔ Kupiec + Christoffersen tests · ✔ Basel traffic-light zoning.

## Next steps
- Add EWMA/GARCH-scaled VaR and show Christoffersen improves.
- Stressed-VaR and an FRTB-style ES with liquidity horizons.
- Feed this book into `rk-04` (EVT/copula tail risk) and `rk-f3` (ML VaR).
