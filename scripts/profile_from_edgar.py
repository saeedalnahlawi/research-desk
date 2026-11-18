#!/usr/bin/env python3
"""Build a telecom valuation profile from SEC EDGAR facts.

Emits profiles/<TICKER>.json in the shape scripts/value_telecom.py expects. Anything EDGAR
does not tag is reported as MISSING rather than guessed — a telco profile with the wrong net
debt produces a confidently wrong fair value, which is worse than no output.

  python3 scripts/profile_from_edgar.py --ticker T --beta 0.70 --price-file data/prices/T.csv
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import urllib.request
from pathlib import Path

CIK = {"T": "0000732717", "VZ": "0000732712", "TMUS": "0001283699", "AAPL": "0000320193"}
UA = {"User-Agent": "Saeed Al-Nahlawi research saeed@nahlawi.com"}


def series(con, ticker, concept):
    rows = con.execute("SELECT end, value FROM annual WHERE ticker=? AND concept=? ORDER BY end", (ticker, concept))
    return {int(r[0][:4]): float(r[1]) for r in rows if r[1] is not None}


def revenue(con, ticker):
    rows = con.execute("SELECT end, revenue FROM revenue_annual WHERE ticker=? ORDER BY end", (ticker,))
    return {int(r[0][:4]): float(r[1]) for r in rows if r[1]}


def shares_out(ticker):
    cik = CIK[ticker]
    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        facts = json.loads(r.read().decode())
    units = next(iter(facts["facts"].get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).values()), [])
    return float(max(units, key=lambda x: x.get("end", ""))["val"]) / 1e6


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--db", default="data/research.db")
    ap.add_argument("--price-file", required=True)
    ap.add_argument("--beta", type=float, default=0.80)
    ap.add_argument("--rf", type=float, default=0.0512)
    ap.add_argument("--erp", type=float, default=0.045)
    ap.add_argument("--g", type=float, default=0.02)
    ap.add_argument("--years", type=int, default=8)
    ap.add_argument("--capex-pct", type=float,
                    help="capex as %% of revenue, if EDGAR does not tag it for this filer")
    ap.add_argument("--out", default="profiles")
    a = ap.parse_args()

    t = a.ticker.upper()
    con = sqlite3.connect(a.db)
    rev = revenue(con, t)
    ebit = series(con, t, "OperatingIncomeLoss")
    da = series(con, t, "DepreciationDepletionAndAmortization")
    capex = series(con, t, "PaymentsToAcquirePropertyPlantAndEquipment")
    tax = series(con, t, "IncomeTaxExpenseBenefit")
    pbt = series(con, t, "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest")
    debt = series(con, t, "LongTermDebt") or series(con, t, "LongTermDebtNoncurrent")
    cash = series(con, t, "CashAndCashEquivalentsAtCarryingValue")
    ni = series(con, t, "NetIncomeLoss")
    liab = series(con, t, "Liabilities")
    eq = (series(con, t, "StockholdersEquity")
          or series(con, t, "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest")
          or series(con, t, "Equity"))
    con.close()

    if not rev or not ebit:
        raise SystemExit(f"{t}: no revenue/EBIT facts — run scripts/fetch_sec.py --tickers {t} first")
    yr = max(rev)

    missing = []
    for name, s in [("revenue", rev), ("EBIT", ebit), ("D&A", da), ("capex", capex),
                    ("tax", tax), ("net income", ni), ("long-term debt", debt), ("cash", cash)]:
        if not s or yr not in s:            # non-empty is not enough: the base year must be present
            missing.append(name)
    r = rev[yr] / 1e6
    ebit_m = ebit[yr] / 1e6
    da_m = da.get(yr, 0.0) / 1e6
    capex_m = capex.get(yr, 0.0) / 1e6
    if ("capex" in missing) and a.capex_pct is not None:
        capex_m = rev[yr] / 1e6 * a.capex_pct
        missing.remove("capex")
        print(f"  capex not tagged by this filer; using {a.capex_pct:.1%} of revenue from --capex-pct")
        capex = {yr: capex_m * 1e6}
    cash_m = cash.get(yr, 0.0) / 1e6
    ni_m = ni.get(yr, 0.0) / 1e6
    debt_m = debt.get(yr, 0.0) / 1e6
    tax_rate = (tax.get(yr, 0.0) / pbt[yr]) if pbt.get(yr) else 0.21
    price = float(Path(a.price_file).read_text().strip().splitlines()[-1].split(",")[1])
    sh = shares_out(t)

    ks = sorted(rev)[-4:]
    cagr = (rev[ks[-1]] / rev[ks[0]]) ** (1 / (len(ks) - 1)) - 1 if len(ks) > 1 else 0.02
    cagr = min(max(cagr, 0.0), 0.08)
    growth = [round(cagr - (cagr - a.g) * (i + 1) / a.years, 4) for i in range(a.years)]

    profile = {
        "_comment": f"Generated from EDGAR facts, FY{yr}. Verify net debt and share count before publishing.",
        "name": f"{t} (EDGAR FY{yr})",
        "ticker": t,
        "currency": "USD",
        "base_year": yr,
        "price": round(price, 2),
        "price_date": "latest local price file",
        "shares_m": round(sh, 1),
        "revenue": round(r, 3),
        "ebitda": round(ebit_m + da_m, 3),
        "da": round(da_m, 3),
        "capex": round(capex_m, 3),
        "tax_rate": round(tax_rate, 3),
        "net_income": round(ni_m, 3),
        "gross_debt": round(debt_m, 3),
        "cash": round(cash_m, 3),
        "net_debt": round(debt_m - cash_m, 3),
        "book_equity": round((eq.get(yr, 0.0) / 1e6) or (liab.get(yr, 0.0) / 1e6), 3),
        "forecast": {
            "years": a.years,
            "revenue_growth": growth,
            "ebitda_margin": round((ebit_m + da_m) / r, 4),
            "capex_pct_of_revenue": round(capex_m / r, 4),
            "da_pct_of_revenue": round(da_m / r, 4),
            "nwc_pct_of_revenue_change": 0.02,
            "mid_year_convention": True,
        },
        "wacc": {"rf": a.rf, "beta": a.beta, "erp": a.erp, "kd": 0.05, "use_market_weights": True},
        "terminal_g": a.g,
        "peers": {"_source": "fill from a peer set before trusting the multiples leg",
                  "discount_for_size_liquidity": 0.0},
    }
    out = Path(a.out) / f"{t.lower()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(profile, indent=2))

    print(f"{t}: FY{yr} revenue {r:,.0f}m | EBITDA {ebit_m+da_m:,.0f}m ({(ebit_m+da_m)/r:.1%}) "
          f"| D&A {da_m:,.0f}m | capex {capex_m:,.0f}m | net income {ni_m:,.0f}m")
    print(f"  debt {debt_m:,.0f}m | cash {cash_m:,.0f}m | net debt {debt_m-cash_m:,.0f}m "
          f"({(debt_m-cash_m)/(ebit_m+da_m):.2f}x EBITDA)")
    print(f"  price {price:,.2f} | shares {sh:,.1f}m | growth path starts {growth[0]:.1%} -> {growth[-1]:.1%}")
    if "capex" in missing:
        print("  FATAL: capex missing and no --capex-pct given. A DCF without capex is meaningless "
              "for a telecom; re-run with --capex-pct (e.g. 0.13 for a US telco) or fix the tag.")
        return 2
    if missing:
        print(f"  MISSING TAGS: {', '.join(missing)} -> fix in the profile before publishing")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
