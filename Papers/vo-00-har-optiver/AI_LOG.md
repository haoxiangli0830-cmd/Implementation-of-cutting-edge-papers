# AI_LOG — vo-00-har-optiver

## 2026-06-15 — Wave 1 build (Claude)
- Added a NEW shared loader `core.data.get_ohlc` (cached daily OHLCV) — reused by
  the frontier vol papers (rough vol, deep vol calib) and microstructure later.
- Chose a **daily Garman-Klass RV proxy** over parsing the 1.7 GB Optiver zip, so
  the build runs free/offline. Documented Optiver as the high-frequency upgrade.
- Implemented HAR as a plain OLS (numpy lstsq) — no need for statsmodels here.
- Strict OOS split (70/30); benchmark = random walk. HAR wins: OOS R² 0.50 vs
  0.40, MSE −17.5%. Coefficients all positive (weekly largest) as in Corsi.
- Next: swap in Optiver intraday RV; add GARCH(1,1) and QLIKE comparison.
