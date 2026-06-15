# spec — eq-f6-price-trends-cnn

**Paper:** Jiang, Kelly & Xiu (2023), "(Re-)Imag(in)ing Price Trends,"
*Journal of Finance* 78(6).

## Claim
Represent a stock's recent history as a black-and-white **image** (OHLC bars,
moving-average line, volume bars) and train a convolutional neural network to
predict the direction of future returns. The CNN — with no hand-crafted
indicators — extracts predictive "price trend" patterns and powers a profitable
long/short portfolio, often outperforming classical momentum.

## What we implement
- Render 20-day OHLCV windows to 40×60 images.
- Label by 20-day forward return sign.
- Train a small CNN; split by time (train <2021, test ≥2021).
- Evaluate OOS accuracy + the long/short return spread (sort by up-probability).

## Data
- yfinance daily OHLCV for 60 large-caps, 2010→present (free), via `core.data.get_ohlc`.

## Benchmark to reproduce
OOS accuracy > 50%; positive long/short spread from image-based predictions.

## Known limits
- 60 stocks ≪ the paper's full CRSP universe → weak magnitude, fast overfitting.
- Simplified renderer and small CPU CNN vs the paper's tuned 64×60 pipeline.
- Reuses `core.models` (seed/device); `core.data.get_ohlc` shared with HAR paper.
