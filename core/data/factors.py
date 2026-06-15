"""Ken French Data Library loader (free academic factor returns).

Downloads and parses the monthly factor CSVs straight from Dartmouth, caches to
parquet. Reused by every equity factor / asset-pricing paper.

    get_french_factors("F-F_Research_Data_5_Factors_2x3")  -> monthly FF5 + RF
    get_french_factors("F-F_Momentum_Factor")              -> monthly MOM
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = _ROOT / "data_store" / "factors"
_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{}_CSV.zip"


def _download_csv(dataset: str) -> str:
    req = Request(_BASE.format(dataset), headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as resp:
        zf = zipfile.ZipFile(io.BytesIO(resp.read()))
    name = zf.namelist()[0]
    return zf.read(name).decode("latin-1")


def _parse_monthly(text: str) -> pd.DataFrame:
    """Pull the monthly block (rows keyed by 6-digit YYYYMM) out of a French CSV."""
    rows, header = [], None
    for line in text.splitlines():
        cells = [c.strip() for c in line.split(",")]
        key = cells[0]
        if header is None:
            # header row is the first line whose remaining cells are non-empty labels
            if key == "" and any(cells[1:]):
                header = cells[1:]
            continue
        if len(key) == 6 and key.isdigit():           # YYYYMM monthly row
            vals = cells[1:1 + len(header)]
            if all(v not in ("", None) for v in vals):
                rows.append([key] + vals)
        elif rows:
            break                                      # reached annual block -> stop
    df = pd.DataFrame(rows, columns=["date"] + header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m") + pd.offsets.MonthEnd(0)
    df = df.set_index("date").astype(float) / 100.0    # percent -> decimal
    return df


def get_french_factors(dataset: str = "F-F_Research_Data_5_Factors_2x3",
                       refresh: bool = False) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fp = CACHE_DIR / f"{dataset}.parquet"
    if fp.exists() and not refresh:
        return pd.read_parquet(fp)
    df = _parse_monthly(_download_csv(dataset))
    df.to_parquet(fp)
    return df
