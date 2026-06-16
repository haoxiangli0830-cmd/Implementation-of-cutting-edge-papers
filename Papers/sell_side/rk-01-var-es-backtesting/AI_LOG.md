# AI_LOG — rk-01-var-es-backtesting

## 2026-06-15 — Risk track launch (Claude)
- New track rk-* for BANK RISK-QUANT (sell-side risk: UBS/Santander/JPM style).
  User wants cutting-edge papers + methods + practices.
- Added shared `core/risk/var.py` (VaR/ES historical/parametric/MC + Kupiec,
  Christoffersen, Basel traffic-light). Reused by all rk-* papers.
- rk-01 on an equal-weight ETF book: historical VaR 2.06% >> parametric 1.42%
  (fat tails); 46 breaches vs 44 expected -> Kupiec PASS but Christoffersen FAIL
  (p~0, clustered) -> the textbook motivation for vol-scaled VaR / ES. Basel GREEN.
- This single result demonstrates real desk practice AND its known limitation —
  a strong portfolio piece for a risk-quant role; ties to the 74-week QMRM curriculum.
- Next rk-*: rk-02 CVA/exposure (sim), rk-03 credit (Merton), rk-04 EVT/copulas,
  rk-f1 Differential ML (Huge-Savine, Danske Bank).
