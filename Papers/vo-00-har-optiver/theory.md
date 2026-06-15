# theory (light) — HAR-RV

Deep dives → 74-week curriculum (time-series weeks: long memory, AR models).

## The idea
Different traders act on different horizons — day traders, swing traders,
long-term investors. Each cares about volatility at their own frequency. HAR
adds up three of them:

    forecast of tomorrow's vol = a little of today's
                               + some of this week's average
                               + some of this month's average

That's the whole model. Three numbers (5-day and 22-day rolling means of daily
vol, plus daily vol itself), one linear regression.

## Why it's clever
Volatility has **long memory**: a spike today still echoes weeks later. The
"proper" way to model that is fractional integration (hard, fiddly). Corsi's
insight: stacking three simple horizons *approximates* long memory almost as well
and is trivial to estimate. Simplicity that works.

## Realized volatility — the measurement
"Realized vol" = volatility actually observed over a period, not implied by
options. Ideally you sum squared *intraday* returns. With only daily bars we use
the **Garman-Klass** estimator, which extracts more information from each day by
using the open, high, low and close (a day that ranged widely was volatile, even
if it closed flat). The Optiver dataset would let us use true intraday data.

## The honest test
We never let the model see the test period while fitting. Beating the
random-walk forecast (RV tomorrow = RV today) *out-of-sample* is the bar — and
HAR clears it (R² 0.50 vs 0.40).
