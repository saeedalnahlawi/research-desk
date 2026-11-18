#!/usr/bin/env python3
"""Fetch daily closes into data/prices/ — Nasdaq public quote API.

Why this source: Yahoo's chart endpoint rate-limits this host hard (429 even via curl), and
Stooq serves a JS challenge. Nasdaq's /api/quote/{sym}/historical answers plain JSON with no
key and covers five years. It needs a browser-ish UA and Accept header.

Use SPY as the market proxy for beta: the Nasdaq endpoint does not serve S&P 500 index
history, and SPY tracks the index closely enough for a beta regression.

  python3 scripts/fetch_prices.py --tickers AAPL KO SPY --years 5
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from datetime import date, timedelta
from pathlib import Path

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")
URL = ("https://api.nasdaq.com/api/quote/{sym}/historical"
       "?assetclass={cls}&fromdate={frm}&limit=9999")


def fetch(symbol: str, years: int, cls: str = "stocks") -> list[tuple[str, float]]:
    frm = (date.today() - timedelta(days=365 * years + 10)).isoformat()
    url = URL.format(sym=symbol, frm=frm, cls=cls)
    last = ""
    for attempt in range(4):
        proc = subprocess.run(
            ["curl", "-sSL", "--max-time", "60", "-A", UA,
             "-H", "Accept: application/json", "-H", "Accept-Language: en-US",
             "-w", "\n%{http_code}", url],
            capture_output=True, text=True)
        body, _, code = proc.stdout.rpartition("\n")
        if proc.returncode == 0 and code.strip() == "200" and body.strip().startswith("{"):
            payload = json.loads(body)
            rows = ((payload.get("data") or {}).get("tradesTable") or {}).get("rows") or []
            if rows:
                out = []
                for r in rows:                     # newest first
                    mm, dd, yy = r["date"].split("/")
                    out.append((date(int(yy), int(mm), int(dd)).isoformat(),
                                float(r["close"].replace("$", "").replace(",", ""))))
                return sorted(out)
            # ETFs (SPY, QQQ) live under a different asset class than single stocks.
            if cls == "stocks":
                time.sleep(1.5)
                return fetch(symbol, years, cls="etf")
            last = "no rows returned"
        else:
            last = f"HTTP {code.strip()} / unexpected body"
        time.sleep(3 + attempt * 3)
    raise RuntimeError(f"{symbol}: fetch failed after 4 attempts ({last})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", required=True)
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--out", default="data/prices")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for sym in a.tickers:
        rows = fetch(sym, a.years)
        path = out / f"{sym.replace('^', 'IDX_')}.csv"
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["date", "close"])
            w.writerows(rows)
        print(f"{sym:6} {len(rows):5} rows  {rows[0][0]} -> {rows[-1][0]}  last {rows[-1][1]:,.2f}  -> {path}")
        time.sleep(1.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
