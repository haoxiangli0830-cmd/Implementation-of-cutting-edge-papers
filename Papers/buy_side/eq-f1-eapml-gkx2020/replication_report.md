# Replication report — eq-f1-eapml-gkx2020 (GKX)

**Verdict: Method replicates.** On a free price/volume characteristic panel, the
nonlinear models (random forest, gradient boosting, neural net) beat linear OLS —
Gu-Kelly-Xiu's central result. Magnitudes are not comparable to the paper (we use
~140 large-caps and price/volume features only, vs their full CRSP + 94
characteristics), but the model ranking and the headline come through.

## Setup
- ~137 US large-caps, 2005→present; 9 price/volume characteristics (momentum,
  reversal, volatility, lottery, illiquidity, size proxy, beta).
- Characteristics rank-normalised cross-sectionally each month (GKX style).
- Time split: train < 2019, test ≥ 2019 (out-of-sample).
- Models: OLS, Random Forest, Gradient Boosting, Neural Net.
- L/S = top-quintile minus bottom-quintile of predicted return, monthly, **gross**.

## Results (out-of-sample)
| Model | OOS R² | L/S Sharpe | L/S ann. |
|---|---|---|---|
| OLS (linear) | 1.96% | 0.41 | 7.0% |
| Random Forest | 2.28% | 0.46 | 7.4% |
| Grad Boosting | 2.09% | 0.65 | 8.3% |
| Neural Net | −1.08% | **0.89** | 10.0% |

See `results/ls_equity.png`.

## What replicates
- **Nonlinear > linear.** RF and gradient boosting beat OLS on OOS R²; gradient
  boosting and the neural net beat it on portfolio Sharpe. This is GKX's core
  finding — flexibility helps because the return/characteristic relationship is
  nonlinear and interactive.

## The instructive nuance
- The **neural net has negative R² but the best Sharpe**. Lesson: *regression
  accuracy and portfolio ranking are different objectives.* The NN predicts the
  return *level* poorly (so R² < 0 vs a zero benchmark) yet **orders** stocks well
  enough that the long/short still works. For trading, ranking is what matters.

## Limitations (why this isn't the paper)
- **Universe**: ~140 current large-caps → survivorship bias and far less breadth
  than full CRSP. Our OOS R² (~2%) is *higher* than the paper's ~0.4% precisely
  because a clean large-cap set with strong momentum features is easier — not
  because our model is better. Not directly comparable.
- **Features**: price/volume only. No value/profitability/investment — those need
  SEC EDGAR fundamentals (the documented upgrade).
- **Costs**: the long/short is gross; quintile monthly rebalancing would lose some
  Sharpe to costs.

## Next steps
- Add EDGAR fundamental characteristics (book-to-market, profitability, accruals).
- Expand the universe (S&P 500 incl. delisted) to kill survivorship bias.
- Run the Deflated Sharpe + transaction costs on the best model's L/S portfolio.
