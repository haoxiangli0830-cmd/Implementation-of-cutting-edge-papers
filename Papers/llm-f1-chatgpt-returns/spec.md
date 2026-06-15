# spec — llm-f1-chatgpt-returns

**Paper:** Lopez-Lira & Tang (2023), "Can ChatGPT Forecast Stock Price Movements?
Return Predictability and Large Language Models." arXiv:2304.07619.

## Claim
A large language model, asked whether a news headline is good or bad for a stock,
produces sentiment scores that predict the stock's next-day return — and the
signal is stronger for smaller, harder-to-arbitrage stocks. LLMs add value over
traditional sentiment methods.

## What we implement
- Sentiment engine = **FinBERT** (free, local) instead of the paid ChatGPT.
- (1) Validate the engine on a labeled benchmark; (2) live cross-sectional
  sentiment snapshot; (3) historical daily long/short sorted on news sentiment.

## Data
- News: yfinance (live, free) for the snapshot; **Finnhub** (free tier, ~1 yr) for
  the historical backtest — needs a free key.
- Prices: yfinance via `core.data.get_prices`.

## Benchmark to reproduce
Positive sentiment → higher next-day returns; a long/short on sentiment earns a
positive Sharpe.

## Known limits
- FinBERT ≠ ChatGPT (weaker reasoning, but the standard free baseline).
- Historical study blocked until a free Finnhub key is provided.
