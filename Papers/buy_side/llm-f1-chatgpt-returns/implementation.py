"""llm-f1-chatgpt-returns — Can ChatGPT Forecast Stock Price Movements?
(Lopez-Lira & Tang, 2023).

Method: score a news headline's sentiment with a language model, then test whether
that sentiment predicts the stock's subsequent return. The paper uses ChatGPT; we
use FinBERT (free, local — no API key needed), which is the standard NLP baseline.

This script has three parts:
  1. VALIDATE the sentiment engine on a labeled benchmark (runs now).
  2. LIVE snapshot: rank today's universe by news sentiment (runs now, free).
  3. HISTORICAL backtest: sentiment -> next-day return long/short
     (needs a free Finnhub key for ~1 yr of news; set FINNHUB_API_KEY).

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.nlp import score_sentiment                            # noqa: E402
from core.data.news import get_recent_news, get_finnhub_news     # noqa: E402
from core.data import get_prices                                 # noqa: E402
from core.evaluation import sharpe                               # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

UNIVERSE = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "JPM", "XOM", "JNJ",
            "WMT", "PG", "HD", "BAC", "DIS", "NFLX", "CRM", "INTC", "AMD", "PFE", "KO"]


def validate_engine(n=400):
    from datasets import load_dataset
    ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="validation")
    import random; random.seed(0)
    idx = random.sample(range(len(ds)), n)
    texts = [ds[i]["text"] for i in idx]; labels = [ds[i]["label"] for i in idx]
    sc = score_sentiment(texts)
    pairs = [(s, l) for s, l in zip(sc, labels) if l in (0, 1)]   # bearish/bullish
    acc = np.mean([(s > 0) == (l == 1) for s, l in pairs])
    return acc, len(pairs)


def live_snapshot():
    news = get_recent_news(UNIVERSE)
    if news.empty:
        print("  (no live news returned)"); return
    news["sent"] = score_sentiment(news["headline"].tolist())
    agg = news.groupby("ticker")["sent"].mean().sort_values()
    print("  most NEGATIVE sentiment:", ", ".join(f"{t}{v:+.2f}" for t, v in agg.head(3).items()))
    print("  most POSITIVE sentiment:", ", ".join(f"{t}{v:+.2f}" for t, v in agg.tail(3).items()))
    news.to_csv(RESULTS / "live_news_sentiment.csv", index=False)


def historical_backtest(api_key):
    end = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    start = end - pd.Timedelta(days=360)
    s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    print(f"  fetching Finnhub news {s} -> {e} ...")
    news = get_finnhub_news(UNIVERSE, s, e, api_key)
    if news.empty:
        print("  no news returned."); return
    news["sent"] = score_sentiment(news["headline"].tolist())
    news["date"] = news["datetime"].dt.tz_convert(None).dt.normalize()
    daily = news.groupby(["date", "ticker"])["sent"].mean().reset_index()

    prices = get_prices(UNIVERSE, start=s)
    rets = prices.pct_change()
    # signal at day t -> trade next day's return
    spreads = []
    for d, g in daily.groupby("date"):
        nd = rets.index[rets.index.searchsorted(d) + 0: rets.index.searchsorted(d) + 1]
        if len(nd) == 0:
            continue
        fwd_day = rets.index[min(rets.index.searchsorted(d) + 1, len(rets.index) - 1)]
        g = g[g["ticker"].isin(rets.columns)]
        if len(g) < 6:
            continue
        hi = g[g["sent"] >= g["sent"].quantile(2/3)]["ticker"]
        lo = g[g["sent"] <= g["sent"].quantile(1/3)]["ticker"]
        r = rets.loc[fwd_day]
        spreads.append(r[hi].mean() - r[lo].mean())
    spreads = pd.Series(spreads).dropna()
    print(f"  long/short days: {len(spreads)}, mean {spreads.mean()*100:+.3f}%/day, "
          f"Sharpe {sharpe(spreads, 252):.2f}")
    spreads.to_csv(RESULTS / "historical_ls.csv")


def main():
    print("\n" + "=" * 60)
    print("llm-f1 — news sentiment -> returns (FinBERT, free)")
    print("=" * 60)

    print("\n[1] Validate sentiment engine on labeled benchmark:")
    acc, n = validate_engine()
    print(f"    FinBERT directional accuracy: {acc:.3f}  (n={n})")

    print("\n[2] Live sentiment snapshot (today's news):")
    live_snapshot()

    print("\n[3] Historical sentiment backtest:")
    key = os.environ.get("FINNHUB_API_KEY")
    if key:
        historical_backtest(key)
    else:
        print("    SKIPPED — no FINNHUB_API_KEY. Get a free key (1 min):")
        print("    https://finnhub.io/register  then set FINNHUB_API_KEY and re-run.")
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
