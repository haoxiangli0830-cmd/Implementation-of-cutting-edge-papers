# Replication report — llm-f1-chatgpt-returns

**Verdict: Directionally replicates on a thin sample.** With a free Finnhub key now
in place, the full pipeline runs: FinBERT sentiment (validated at 84% accuracy)
sorted into a daily long/short earns **+0.087%/day, Sharpe 1.44** — the right sign
and a strong ratio, *but on only 25 qualifying days*, because Finnhub's free tier
returns sparse history. Encouraging, not yet robust.

## Historical result (Finnhub free tier, 20 large-caps, ~1 yr window)
| Metric | Value |
|---|---|
| Long/short days | 25 |
| Mean return | +0.087% / day |
| Annualised Sharpe | 1.44 |

The positive sign (positive-sentiment stocks beat negative-sentiment stocks next
day) matches Lopez-Lira & Tang. **Caveat:** 25 days is far too few to trust the
1.44 Sharpe — the free tier only densely covers recent weeks, so most of the year
had too few simultaneously-covered names. Treat this as "pipeline proven + early
positive signal," not a verified edge.

## Method (vs the paper)
- Lopez-Lira & Tang prompt **ChatGPT** to rate a headline's implication for the
  stock, then test if that rating predicts returns.
- We use **FinBERT** (free, local, no API key) as the sentiment engine — the
  standard NLP baseline these LLM papers benchmark against. (Your Claude
  subscription can't be scripted, so a local model is the free path.)

## What runs now
1. **Engine validation** — on the `twitter-financial-news-sentiment` benchmark,
   FinBERT scores **0.84 directional accuracy** (bullish vs bearish). The sentiment
   signal is real and reliable.
2. **Live snapshot** — fetched today's headlines for 20 large-caps (free via
   yfinance) and ranked by sentiment, e.g. most-positive AMD/AMZN/HD,
   most-negative CRM/AAPL. Proves the full text → score → rank pipeline works.

## The data limitation (why the sample is thin)
- Finnhub's **free tier** densely covers only recent weeks of company news, so over
  a 1-year window only ~25 days had ≥6 of our 20 names covered simultaneously.
- To get a robust result: use a fuller free news corpus (**FNSPID** on HuggingFace,
  millions of articles) or Finnhub's paid history; then re-run — the pipeline is
  unchanged. The key is stored in the program-root `.env` (auto-loaded).

## Reusable assets built here
- `core/nlp` — FinBERT sentiment + sentence-transformer embeddings (shared with
  `llm-f3` and `cr-f2`).
- `core/data/news.py` — Finnhub (historical) + yfinance (live) news loaders.

## Next steps
- Add a free Finnhub key → run the historical long/short and apply the rigor layer.
- Compare FinBERT vs a finance-tuned local LLM (Ollama) to approximate the paper's
  ChatGPT setup more closely.
