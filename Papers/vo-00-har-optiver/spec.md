# spec — vo-00-har-optiver

**Paper:** Corsi (2009), "A Simple Approximate Long-Memory Model of Realized
Volatility (HAR-RV)," *Journal of Financial Econometrics* 7(2).
**Companion data:** Optiver Realized Volatility Prediction (Kaggle).

## Claim
Realized volatility can be forecast accurately with a simple regression on
volatility measured over three horizons — daily, weekly, monthly — which mimics
the "heterogeneous market" of traders acting at different frequencies and
reproduces volatility's long-memory persistence without fractional integration.

## Model
    RV[t+1] = b0 + b_d*RV_d[t] + b_w*RV_w[t] + b_m*RV_m[t] + e
where RV_w, RV_m are trailing 5- and 22-day averages of daily RV.

## What we implement
- Daily RV proxy via the **Garman-Klass** OHLC estimator (efficient daily vol).
- OLS fit on a 70% train split; forecast the 30% test split out-of-sample.
- Benchmark vs the random-walk forecast (RV[t+1] = RV[t]); report R² and MSE.

## Data
- yfinance daily OHLC for ^GSPC, 1990→present (free), via `core.data.get_ohlc`.

## Benchmark to reproduce
Positive daily/weekly/monthly coefficients; HAR beats the random walk OOS.

## Known limits
- Daily-bar Garman-Klass ≠ true intraday realised vol → Optiver data is the
  high-frequency upgrade path.
