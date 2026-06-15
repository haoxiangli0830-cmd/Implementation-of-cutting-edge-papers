"""Price loader with on-disk parquet caching.

One job: turn a list of tickers into a tidy wide DataFrame of adjusted close
prices, caching each ticker so repeated backtests are fast and offline.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

# data_store lives at the program root: <root>/data_store/prices/<TICKER>.parquet
_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = _ROOT / "data_store" / "prices"


def _load_one(ticker: str, start: str, end: str | None, refresh: bool) -> pd.Series:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fp = CACHE_DIR / f"{ticker}.parquet"
    if fp.exists() and not refresh:
        s = pd.read_parquet(fp).iloc[:, 0]
    else:
        import yfinance as yf

        df = yf.download(
            ticker, start="1990-01-01", end=None,
            auto_adjust=True, progress=False, threads=False,
        )
        if df.empty:
            raise ValueError(f"No data returned for {ticker!r}")
        s = df["Close"]
        if isinstance(s, pd.DataFrame):       # yfinance sometimes returns a frame
            s = s.iloc[:, 0]
        s.name = ticker
        s.to_frame().to_parquet(fp)
    s.index = pd.to_datetime(s.index)
    s = s.loc[start:] if start else s
    s = s.loc[:end] if end else s
    return s


def get_prices(
    tickers: list[str],
    start: str = "2000-01-01",
    end: str | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """Return a wide DataFrame of adjusted close prices (columns = tickers)."""
    cols = {t: _load_one(t, start, end, refresh) for t in tickers}
    df = pd.DataFrame(cols).sort_index()
    return df


def monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Month-end simple returns from a daily price frame."""
    monthly = prices.resample("ME").last()
    return monthly.pct_change()


def get_ohlc(ticker: str, start: str = "1990-01-01", refresh: bool = False) -> pd.DataFrame:
    """Single-ticker daily OHLCV frame (cached). Used by vol / microstructure work."""
    cache = _ROOT / "data_store" / "ohlcv"
    cache.mkdir(parents=True, exist_ok=True)
    fp = cache / f"{ticker}.parquet"
    if fp.exists() and not refresh:
        df = pd.read_parquet(fp)
    else:
        import yfinance as yf

        df = yf.download(ticker, start="1990-01-01", auto_adjust=True,
                         progress=False, threads=False)
        if df.empty:
            raise ValueError(f"No OHLC data for {ticker!r}")
        if isinstance(df.columns, pd.MultiIndex):       # collapse yfinance MI cols
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.to_parquet(fp)
    df.index = pd.to_datetime(df.index)
    return df.loc[start:]
