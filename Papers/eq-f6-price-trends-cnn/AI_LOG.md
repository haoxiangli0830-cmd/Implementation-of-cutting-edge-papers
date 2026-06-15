# AI_LOG — eq-f6-price-trends-cnn

## 2026-06-15 — Wave 1 build (Claude)
- Reused `core.data.get_ohlc` (from HAR paper) and `core.models.set_seed`.
- Wrote a chart renderer (OHLC bars + 5d MA line + volume) -> 40x60 uint8 images;
  25k samples over 60 large-caps. Small CNN (2 conv + FC), strict time split
  (train <2021, test >=2021).
- Bugs fixed: (1) dates came back as object Timestamps -> pd.to_datetime; (2) the
  comparison returns a plain ndarray, dropped the bogus .to_numpy().
- Result: OOS accuracy 0.54-0.56 (> coin flip), L/S spread Sharpe 0.28. Overfits
  after epoch 1 -> reported honestly. Core claim (images carry signal) holds; the
  magnitude is small due to the 60-stock universe.
- Next: full CRSP/S&P500 universe, early stopping, match the 64x60 spec, add the
  Deflated-Sharpe portfolio test.
