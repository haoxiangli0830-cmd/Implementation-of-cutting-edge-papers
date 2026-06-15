# Replication report — eq-f6-price-trends-cnn

**Verdict: Core claim replicates, weakly.** A CNN reading *images* of price charts
predicts next-month direction better than a coin flip out-of-sample (53.8–55.7%
accuracy) and produces a positive long/short spread. But the effect is small on
our 60-stock universe and the model overfits within a couple of epochs — both
expected given we use a fraction of the paper's data.

## Setup
- 60 large-cap US stocks, 2010–present, 20-day OHLC+volume charts rendered to
  40×60 black/white images (25,330 samples).
- Label = sign of the 20-day forward return.
- **Time split** (no leakage): train < 2021, test ≥ 2021.
- Small CNN (2 conv + FC), trained on CPU.

## Results (out-of-sample, test ≥ 2021)
| Metric | Value |
|---|---|
| Classification accuracy | 0.54–0.56 (peak 0.557) |
| Long/short 20-day spread | +0.15% per rebalance |
| Annualised Sharpe of spread | 0.28 |
| Rebalances | 135 |

See `results/sample_charts.png` (what the CNN "sees") and `results/ls_spread.png`.

## What replicates
- **Images of price trends contain predictive information.** Accuracy is reliably
  above 50% and the long/short spread is positive — the paper's central, initially
  surprising claim. A vision model with no hand-crafted features finds tradable
  structure in raw chart pixels.

## What's weak / didn't fully replicate
- **Magnitude.** The paper reports strong, highly significant long/short returns;
  ours is a modest Sharpe 0.28. Causes: (a) 60 stocks vs the paper's full CRSP
  universe (thousands) — far fewer training images and far less cross-sectional
  breadth; (b) a simplified image renderer; (c) a small CPU-trained CNN.
- **Overfitting.** Test accuracy peaked at epoch 1 (0.557) then drifted down — the
  model memorises with so little data. The paper relies on a huge sample +
  regularisation to avoid this.

## Next steps to strengthen
- Expand to the full S&P 500 / CRSP universe (10–100× more images).
- Add early stopping + stronger regularisation; match the paper's 64×60 image spec.
- Try the 5-day and 60-day image/horizon variants the paper studies.
- Build a proper tradable portfolio (decile sorts, monthly) and run the rigor
  layer (Deflated Sharpe) on it.
