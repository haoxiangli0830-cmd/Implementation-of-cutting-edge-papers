# AI_LOG — llm-f1-chatgpt-returns

## 2026-06-15 — Wave 2 / LLM track start (Claude)
- User has no Anthropic API key (subscription can't be scripted) -> use FREE LOCAL
  models. Built `core/nlp` (FinBERT sentiment + sentence-transformer embeddings),
  reused by llm-f3 and cr-f2.
- Validated FinBERT: 0.84 directional accuracy on twitter-financial-news-sentiment.
- Data reality: NO API keys anywhere in the user's projects (only .env.example).
  yfinance news = last ~1-2 days only -> good for a live snapshot, not a backtest.
- Built `core/data/news.py` (Finnhub historical + yfinance live). llm-f1 runs the
  validation + a live sentiment ranking now; the historical long/short path is
  written and waits on a free FINNHUB_API_KEY.
- Honest status: engine done + validated; historical replication pending a free
  Finnhub key (1-min registration).
- Financial PhraseBank wouldn't load (datasets 4.x dropped script datasets) ->
  validated on the parquet twitter dataset instead.
- Next: get Finnhub key -> run historical L/S + rigor layer; then llm-f3 (embeddings).
