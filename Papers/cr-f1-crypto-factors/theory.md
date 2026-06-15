# theory (light) — Crypto factors

Same factor-model logic as [[eq-00-fama-french]] — see that theory note for the
core idea. Crypto-specific points only here.

## Why weekly, not monthly
Crypto trades 24/7 and moves fast; the paper finds the momentum effect lives at
the **1–4 week** horizon (equity momentum is 3–12 *months*). So we resample to
weekly and use a 3-week look-back.

## The three factors
- **Market** = average return of all coins (the crypto "beta"). Huge premium,
  huge drawdowns (~80%).
- **Size** = small minus big. We proxy size by **dollar volume** (price×volume)
  because historical market cap isn't in yfinance. A real build uses CoinGecko caps.
- **Momentum** = long recent winners, short recent losers, cross-sectionally.

## The one honesty mechanism that mattered here
The **Deflated Sharpe Ratio**. Raw, the best look-back (3wk) had Sharpe 0.25 —
tempting to report. But we tried 4 look-backs; deflating for that gives 0.46,
i.e. *no real edge*. Without this check we'd have "found" a crypto momentum
strategy that is actually noise. This is the single most important habit in
quant research: penalise yourself for every variant you tried.
