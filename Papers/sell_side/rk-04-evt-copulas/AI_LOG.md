# AI_LOG — rk-04-evt-copulas

## 2026-06-15 — Risk track (Claude)
- EVT POT: GPD fit (scipy.genpareto) to losses over the 95th pct; VaR/ES at 99% & 99.9%.
- Copulas: Gaussian vs Student-t (nu=4), simulated with empirical margins (manual
  Cholesky + chi2 mixing), compared book 99% VaR.
- Result: at 99% normal~EVT~empirical (~2.4%); at 99.9% normal 2.65% vs EVT 5.07% /
  empirical 5.39% -> normal understates extreme tail ~2x (heavy tail, xi>0). t-copula
  VaR +3% vs Gaussian at 99% (gap widens deeper in tail).
- Used the rk-01 ETF book idea (5 assets). All from cached prices.
- Next: estimate t-copula nu; copula VaR at 99.9%; feed EVT-ES into FRTB reporting.
