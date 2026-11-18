#!/usr/bin/env python3
"""Estimate equity beta by regressing a stock's returns on a benchmark's.

Beta = cov(stock, index) / var(index). Reported with R-squared so you can see how much
of the stock's movement the index actually explains — a beta with a low R² is not an
input worth trusting.

  python3 scripts/estimate_beta.py --stock data/prices/AAPL.csv --index data/prices/IDX_GSPC.csv
  python3 scripts/estimate_beta.py ... --weekly      # less noisy, fewer observations
"""
from __future__ import annotations

import argparse
import csv
import math
from datetime import date
from pathlib import Path


def load(path: Path) -> dict[str, float]:
    with path.open() as fh:
        return {r["date"]: float(r["close"]) for r in csv.DictReader(fh)}


def returns(series: dict[str, float], weekly: bool) -> dict[str, float]:
    dates = sorted(series)
    if weekly:
        # keep the last observation of each ISO week
        keep = {}
        for d in dates:
            y, w, _ = date.fromisoformat(d).isocalendar()
            keep[(y, w)] = d
        dates = [keep[k] for k in sorted(keep)]
    out = {}
    for prev, cur in zip(dates, dates[1:]):
        out[cur] = series[cur] / series[prev] - 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--weekly", action="store_true")
    a = ap.parse_args()

    s = returns(load(Path(a.stock)), a.weekly)
    m = returns(load(Path(a.index)), a.weekly)
    common = sorted(set(s) & set(m))
    if len(common) < 30:
        raise SystemExit(f"only {len(common)} overlapping observations — need at least 30")

    xs = [m[d] for d in common]
    ys = [s[d] for d in common]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)
    varx = sum((x - mx) ** 2 for x in xs) / (n - 1)
    vary = sum((y - my) ** 2 for y in ys) / (n - 1)
    beta = cov / varx
    alpha_daily = my - beta * mx
    r2 = (cov ** 2) / (varx * vary)

    print(f"observations      {n}  ({'weekly' if a.weekly else 'daily'})  {common[0]} -> {common[-1]}")
    print(f"beta              {beta:.3f}")
    print(f"alpha (daily)     {alpha_daily*100:+.4f}%")
    print(f"R-squared         {r2:.3f}")
    print(f"stock vol (ann.)   {math.sqrt(vary)*math.sqrt(252 if not a.weekly else 52)*100:.1f}%")
    print(f"index vol (ann.)   {math.sqrt(varx)*math.sqrt(252 if not a.weekly else 52)*100:.1f}%")
    if r2 < 0.20:
        print("WARNING: low R-squared — the index explains little of this stock's movement; "
              "treat beta as a weak input.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
