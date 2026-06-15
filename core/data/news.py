"""News loaders for the LLM-track papers.

- get_recent_news(tickers): FREE, no key — yfinance, but only the last day or two.
- get_finnhub_news(tickers, start, end): historical (~1 yr on the free tier),
  needs a free Finnhub key (env FINNHUB_API_KEY or passed in). Cached to parquet.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
CACHE = _ROOT / "data_store" / "news"


def get_recent_news(tickers: list[str]) -> pd.DataFrame:
    """Most-recent headlines per ticker (free, yfinance). Live snapshot only."""
    import yfinance as yf
    rows = []
    for tk in tickers:
        try:
            items = yf.Ticker(tk).news or []
        except Exception:
            continue
        for it in items:
            c = it.get("content", it)
            title = c.get("title")
            ts = c.get("pubDate") or c.get("providerPublishTime")
            if title and ts:
                rows.append({"ticker": tk, "datetime": pd.to_datetime(ts, utc=True),
                             "headline": title})
    return pd.DataFrame(rows)


def get_finnhub_news(tickers: list[str], start: str, end: str,
                     api_key: str | None = None) -> pd.DataFrame:
    """Historical company news via Finnhub (free tier ~1 yr). Cached per ticker."""
    api_key = api_key or os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        raise RuntimeError("No Finnhub key. Set FINNHUB_API_KEY or pass api_key. "
                           "Free registration: https://finnhub.io/register")
    import requests
    CACHE.mkdir(parents=True, exist_ok=True)
    frames = []
    for tk in tickers:
        fp = CACHE / f"{tk}_{start}_{end}.parquet"
        if fp.exists():
            frames.append(pd.read_parquet(fp)); continue
        url = ("https://finnhub.io/api/v1/company-news"
               f"?symbol={tk}&from={start}&to={end}&token={api_key}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df = df[["datetime", "headline"]].copy()
            df["datetime"] = pd.to_datetime(df["datetime"], unit="s", utc=True)
            df["ticker"] = tk
            df.to_parquet(fp)
            frames.append(df)
        time.sleep(1.1)                       # free-tier rate limit
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
