# theory (light) — Price Trends as images (CNN)

Deep dives → 74-week curriculum (ML-for-risk weeks: neural nets, CNNs).

## The surprising idea
Technical analysts have always *looked at charts* and claimed to see patterns.
Most academics dismissed this. This paper asks: if there's real signal in the
*picture*, give the picture to the tool built for pictures — a convolutional
neural network (the same architecture that recognises cats in photos).

## How it works
1. **Render**: turn 20 days of OHLC + volume into a small black-and-white image —
   vertical bars for each day's high-low range, ticks for open/close, a moving
   average line, volume bars along the bottom. (See `results/sample_charts.png`.)
2. **Label**: did the stock go up or down over the next 20 days?
3. **Train a CNN** to classify up vs down from the image alone.
4. **Trade**: each period, rank stocks by the CNN's predicted up-probability; buy
   the top group, short the bottom.

## Why a CNN (not a normal regression)
A CNN slides small filters across the image, learning local visual motifs
(a breakout, a pullback, a volume spike) regardless of *where* they appear — it
discovers the "patterns" instead of you specifying them.

## The honesty rule that matters most here
**Split by time, never randomly.** We train only on pre-2021 charts and test on
2021+. If you shuffled randomly, tomorrow's charts could leak into training and
you'd report a fantasy accuracy. With deep nets it's also easy to *overfit* — ours
peaked at epoch 1 then got worse on the test set, a textbook sign there isn't
enough data. Real signal, weakly, is the honest read.
