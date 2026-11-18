#!/usr/bin/env python3
"""Fetch US-listed company financials from SEC EDGAR into tidy CSV files.

Free, no API key. SEC requires a descriptive User-Agent with contact details.

  python3 scripts/fetch_sec.py --tickers AAPL KO
  python3 scripts/fetch_sec.py --tickers AAPL --out data/raw

Output: data/raw/<TICKER>_facts.csv with one row per concept-period-value.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Saeed Al-Nahlawi research saeed@nahlawi.com"}
TICKER_CIK = {
    "AAPL": "0000320193",
    "KO": "0000021344",
    "MSFT": "0000789019",
    "JPM": "0000019617",
    "AT&T": "0000732717",
    "T": "0000732717",
}
# Ticker -> expected name fragment. A wrong CIK silently returns another company's
# data, so the fetched entityName must match this or the script refuses to write.
EXPECTED_NAME = {
    "AAPL": "APPLE",
    "KO": "COCA",
    "MSFT": "MICROSOFT",
    "JPM": "JPMORGAN",
    "T": "AT&T",
}
CONCEPTS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "CostOfRevenue",
    "GrossProfit",
    "OperatingIncomeLoss",
    "NetIncomeLoss",
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue",
    "LongTermDebtNoncurrent",
    "InterestExpense",
    "EarningsPerShareDiluted",
]


def fetch(cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def tidy(ticker: str, payload: dict) -> list[dict]:
    rows = []
    gaap = payload.get("facts", {}).get("us-gaap", {})
    for concept in CONCEPTS:
        block = gaap.get(concept)
        if not block:
            continue
        for unit, points in block.get("units", {}).items():
            for p in points:
                # Keep only filed annual/quarterly facts with a period end.
                if not p.get("end"):
                    continue
                rows.append({
                    "ticker": ticker,
                    "concept": concept,
                    "unit": unit,
                    "start": p.get("start", ""),
                    "end": p["end"],
                    "value": p.get("val"),
                    "fy": p.get("fy", ""),
                    "fp": p.get("fp", ""),
                    "form": p.get("form", ""),
                    "filed": p.get("filed", ""),
                    "frame": p.get("frame", ""),
                })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", required=True)
    ap.add_argument("--out", default="data/raw")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    for t in a.tickers:
        t = t.upper()
        cik = TICKER_CIK.get(t)
        if not cik:
            print(f"{t}: no CIK in map — add it to TICKER_CIK", file=sys.stderr)
            continue
        payload = fetch(cik)
        name = (payload.get("entityName") or "").upper()
        expect = EXPECTED_NAME.get(t, "")
        if expect and expect not in name:
            print(f"{t}: REFUSED — CIK {cik} returned '{payload.get('entityName')}', "
                  f"expected a name containing '{expect}'. Fix TICKER_CIK.", file=sys.stderr)
            continue
        rows = tidy(t, payload)
        path = out / f"{t}_facts.csv"
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["ticker"])
            w.writeheader()
            w.writerows(rows)
        print(f"{t:6} {payload.get('entityName','?'):35} rows={len(rows):5} -> {path}")
        time.sleep(0.3)  # be polite to SEC
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
