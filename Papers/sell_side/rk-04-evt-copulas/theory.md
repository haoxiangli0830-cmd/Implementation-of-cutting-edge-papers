# theory (light) — EVT & copulas

Deep dives → 74-week QMRM curriculum (EVT, copulas, dependence weeks).

## Why normal fails in the tail
The normal distribution has thin tails — it says a 5-sigma day "never" happens. Real
markets have them every few years. So normal VaR is fine for ordinary days and
badly wrong for the rare, catastrophic ones.

## EVT — model the tail, don't assume it
Extreme Value Theory says: forget the whole distribution, focus only on the
**exceedances** over a high threshold. A deep theorem says those exceedances follow
a **Generalised Pareto Distribution** almost regardless of the underlying. Fit that
GPD and you get an honest VaR/ES far out in the tail.
- **ξ (tail index)** is the key number: ξ > 0 = heavy tail (power-law decay), much
  fatter than normal. Our data has ξ > 0, which is why EVT 99.9% VaR (~5%) dwarfs the
  normal estimate (~2.7%).

## Copulas — dependence, separated from the margins
A copula splits a joint distribution into "what each asset does on its own"
(margins) and "how they move together" (the copula). This lets you keep realistic
fat-tailed margins *and* choose the dependence:
- **Gaussian copula**: zero tail dependence — extreme joint moves only by chance.
  (Infamously, this assumption helped mis-price CDOs before 2008.)
- **Student-t copula**: positive tail dependence — when one asset crashes, others are
  *more likely* to crash too. More realistic for a crisis.

## The lesson
Tail risk has two sources: each asset's own fat tails (EVT) **and** their tendency to
fail together (copulas). Normal VaR ignores both. Diversification that looks great in
calm markets can evaporate in a crash — which is exactly what a risk desk must
capital against.
