"""eq-f6-price-trends-cnn — (Re-)Imag(in)ing Price Trends
(Jiang, Kelly & Xiu, 2023, Journal of Finance).

Idea: render each stock's recent price history as a small black-and-white IMAGE
(OHLC bars + moving-average line + volume), then train a convolutional neural
network — the kind used for vision — to predict whether the stock goes up or down
next. Sort stocks by the CNN's up-probability into a long/short portfolio.

We render 20-day charts, label by the 20-day forward return, split by time
(train < 2021, test >= 2021), and measure both classification accuracy and the
out-of-sample long/short return spread.

Run:  python implementation.py   ->  results/   (trains a CNN on CPU, ~few min)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import torch                                                  # noqa: E402
import torch.nn as nn                                         # noqa: E402
from core.data.prices import get_ohlc                         # noqa: E402
from core.models import set_seed                              # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

WINDOW, HORIZON, STRIDE = 20, 20, 10          # 20-day image -> 20-day forward return
HP, HV, COLW = 32, 8, 3                        # price-rows, volume-rows, cols/day
W = WINDOW * COLW
SPLIT_DATE = "2021-01-01"

UNIVERSE = [
    "AAPL", "MSFT", "JNJ", "JPM", "XOM", "PG", "KO", "PFE", "WMT", "CVX",
    "MRK", "INTC", "CSCO", "ORCL", "IBM", "MCD", "DIS", "HD", "BA", "CAT",
    "MMM", "AXP", "VZ", "T", "WFC", "C", "BAC", "GS", "UNH", "ABT",
    "AMGN", "TXN", "QCOM", "NKE", "LOW", "SBUX", "COST", "HON", "UPS", "GE",
    "AMZN", "GOOGL", "META", "NVDA", "ADBE", "CRM", "PEP", "ABBV", "TMO", "ACN",
    "AVGO", "MDT", "DHR", "LIN", "NEE", "PM", "RTX", "UNP", "LMT", "SPGI",
]


def render(o, h, l, c, v) -> np.ndarray:
    """Render one OHLCV window to an (HP+HV) x W black/white image (uint8 0/1)."""
    img = np.zeros((HP + HV, W), dtype=np.uint8)
    pmin, pmax = l.min(), h.max()
    if pmax <= pmin:
        return img
    ma = pd.Series(c).rolling(5, min_periods=1).mean().values

    def row(p):                                    # price -> pixel row (0 = top)
        return int((HP - 1) * (1 - (p - pmin) / (pmax - pmin)))

    vmax = v.max() if v.max() > 0 else 1.0
    for d in range(WINDOW):
        x = d * COLW
        img[row(h[d]):row(l[d]) + 1, x + 1] = 1     # high-low bar (center col)
        img[row(o[d]), x] = 1                        # open tick (left)
        img[row(c[d]), x + 2] = 1                    # close tick (right)
        img[row(ma[d]), x:x + COLW] = 1              # moving-average line
        vh = int((HV - 1) * v[d] / vmax)             # volume bar (bottom block)
        if vh > 0:
            img[HP + HV - vh:HP + HV, x:x + COLW] = 1
    return img


def build_dataset():
    X, y, dates, tickers = [], [], [], []
    for tk in UNIVERSE:
        try:
            df = get_ohlc(tk, start="2009-06-01")
        except Exception:
            continue
        o, h, l, c, v = (df[col].values for col in ("Open", "High", "Low", "Close", "Volume"))
        idx = df.index
        for t in range(WINDOW, len(df) - HORIZON, STRIDE):
            w = slice(t - WINDOW, t)
            fwd = c[t + HORIZON - 1] / c[t - 1] - 1
            if not np.isfinite(fwd):
                continue
            X.append(render(o[w], h[w], l[w], c[w], v[w]))
            y.append(1.0 if fwd > 0 else 0.0)
            dates.append(idx[t]); tickers.append(tk)
    X = np.asarray(X, dtype=np.float32)[:, None, :, :]        # N,1,H,W
    return X, np.asarray(y, np.float32), np.asarray(dates), np.asarray(tickers)


class ChartCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.head = nn.Sequential(nn.Flatten(), nn.LazyLinear(64), nn.ReLU(),
                                  nn.Dropout(0.3), nn.Linear(64, 1))

    def forward(self, x):
        return self.head(self.conv(x)).squeeze(1)


def main():
    set_seed(0)
    print("  building image dataset (rendering charts)...")
    X, y, dates, tickers = build_dataset()
    dates = pd.to_datetime(dates)
    train = np.asarray(dates < pd.Timestamp(SPLIT_DATE))
    print(f"  samples: {len(y)}  (train {train.sum()}, test {(~train).sum()}), image {X.shape[2]}x{X.shape[3]}")

    Xtr = torch.tensor(X[train]); ytr = torch.tensor(y[train])
    Xte = torch.tensor(X[~train]); yte = torch.tensor(y[~train])

    net = ChartCNN()
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    n, bs = len(Xtr), 128
    for epoch in range(5):
        net.train(); perm = torch.randperm(n)
        for i in range(0, n, bs):
            b = perm[i:i + bs]
            opt.zero_grad()
            loss = lossf(net(Xtr[b]), ytr[b])
            loss.backward(); opt.step()
        net.eval()
        with torch.no_grad():
            acc = ((net(Xte) > 0).float() == yte).float().mean().item()
        print(f"  epoch {epoch+1}/5  test accuracy {acc:.3f}")

    # --- out-of-sample long/short by predicted up-probability ------------------
    with torch.no_grad():
        prob = torch.sigmoid(net(Xte)).numpy()
    te = pd.DataFrame({"date": dates[~train], "prob": prob,
                       "fwd": [None] * (~train).sum()})
    # recover forward returns for the test rows
    fwd = []
    cache = {}
    for tk in np.unique(tickers[~train]):
        cache[tk] = get_ohlc(tk, start="2009-06-01")["Close"]
    j = 0
    for k in range(len(dates)):
        if not train[k]:
            cser = cache[tickers[k]]
            pos = cser.index.get_loc(dates[k])
            fwd.append(cser.iloc[pos + HORIZON - 1] / cser.iloc[pos - 1] - 1
                       if pos + HORIZON - 1 < len(cser) else np.nan)
            j += 1
    te["fwd"] = fwd
    te = te.dropna()

    spreads = []
    for d, g in te.groupby("date"):
        if len(g) < 6:
            continue
        hi = g[g["prob"] >= g["prob"].quantile(2 / 3)]["fwd"].mean()
        lo = g[g["prob"] <= g["prob"].quantile(1 / 3)]["fwd"].mean()
        spreads.append(hi - lo)
    spreads = np.array(spreads)
    periods_per_year = 252 / STRIDE
    sharpe = spreads.mean() / spreads.std() * np.sqrt(periods_per_year) if spreads.std() else np.nan

    print("\n" + "=" * 60)
    print("eq-f6-price-trends-cnn — out-of-sample (test >= 2021)")
    print("=" * 60)
    print(f"  test classification accuracy : {((prob>0.5)==(yte.numpy()>0.5)).mean():.3f}  (50% = coin flip)")
    print(f"  long/short 20-day return spread: mean {spreads.mean()*100:+.2f}% per rebalance")
    print(f"  annualised Sharpe of the spread: {sharpe:.2f}")
    print(f"  rebalances: {len(spreads)}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(11, 3))
    for ax, k in zip(axes, np.random.default_rng(0).choice(len(X), 4, replace=False)):
        ax.imshow(X[k, 0], cmap="gray_r"); ax.axis("off")
        ax.set_title("up" if y[k] > 0 else "down", fontsize=9)
    fig.suptitle("Sample rendered price-chart images (CNN inputs)")
    fig.tight_layout(); fig.savefig(RESULTS / "sample_charts.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    ax2.plot(np.cumsum(spreads), lw=1.3)
    ax2.set_title("Cumulative long/short 20-day return spread (out-of-sample)")
    ax2.set_ylabel("Cumulative spread"); ax2.grid(True, alpha=0.3)
    fig2.tight_layout(); fig2.savefig(RESULTS / "ls_spread.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
