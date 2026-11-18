#!/usr/bin/env python3
"""FCFF / DCF valuation for non-financial companies, using EDGAR fundamentals.

For banks and insurers use scripts/value_bank.py instead — free cash flow to the firm has
no meaning when interest expense is an operating cost.

Pipeline: EDGAR facts (in data/research.db) -> forecast -> WACC -> EV -> equity -> per share.

  python3 scripts/value_dcf.py --ticker AAPL --rf 0.0512 --erp 0.045 --g 0.025
  python3 scripts/value_dcf.py --ticker KO --beta 0.60        # override the regression

WACC inputs: risk-free from the US Treasury curve (FRED DGS10), equity risk premium as an
argument, beta estimated by regression (scripts/estimate_beta.py) or passed in, cost of debt
from interest expense / total debt with a 4% floor.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import urllib.request
from pathlib import Path

CIK = {"AAPL": "0000320193", "KO": "0000021344", "MSFT": "0000789019"}
UA = {"User-Agent": "Saeed Al-Nahlawi research saeed@nahlawi.com"}


def annual(con: sqlite3.Connection, ticker: str, concept: str) -> dict[int, float]:
    """Latest full-year value per fiscal year for one concept."""
    rows = con.execute(
        "SELECT end, value FROM annual WHERE ticker = ? AND concept = ? ORDER BY end", (ticker, concept))
    return {int(r[0][:4]): float(r[1]) for r in rows if r[1] is not None}


def revenue(con: sqlite3.Connection, ticker: str) -> dict[int, float]:
    rows = con.execute("SELECT end, revenue FROM revenue_annual WHERE ticker = ? ORDER BY end", (ticker,))
    return {int(r[0][:4]): float(r[1]) for r in rows if r[1]}


def shares_outstanding(ticker: str) -> float:
    """Share count from the EDGAR cover page (dei), in millions."""
    cik = CIK[ticker]
    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        facts = json.loads(r.read().decode())
    block = facts["facts"].get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
    units = next(iter(block.get("units", {}).values()), [])
    latest = max(units, key=lambda p: p.get("end", ""))
    return float(latest["val"]) / 1e6


def last_price(path: Path) -> float:
    lines = path.read_text().strip().splitlines()
    return float(lines[-1].split(",")[1])


def cagr(series: dict[int, float], years: int = 3) -> float:
    ks = sorted(series)[-(years + 1):]
    if len(ks) < 2:
        return 0.0
    first, last = series[ks[0]], series[ks[-1]]
    return (last / first) ** (1 / (len(ks) - 1)) - 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--db", default="data/research.db")
    ap.add_argument("--prices", default="data/prices")
    ap.add_argument("--rf", type=float, default=0.0512, help="risk-free (10y UST, FRED DGS10)")
    ap.add_argument("--erp", type=float, default=0.045)
    ap.add_argument("--beta", type=float, default=None, help="override the regression estimate")
    ap.add_argument("--g", type=float, default=0.025, help="terminal growth")
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--nwc", type=float, default=0.03, help="dNWC as %% of revenue change")
    a = ap.parse_args()

    t = a.ticker.upper()
    con = sqlite3.connect(a.db)
    rev = revenue(con, t)
    ebit = annual(con, t, "OperatingIncomeLoss")
    da = annual(con, t, "DepreciationDepletionAndAmortization")
    capex = annual(con, t, "PaymentsToAcquirePropertyPlantAndEquipment")
    tax = annual(con, t, "IncomeTaxExpenseBenefit")
    pbt = annual(con, t, "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest")
    interest = annual(con, t, "InterestExpense")
    debt = annual(con, t, "LongTermDebt") or annual(con, t, "LongTermDebtNoncurrent")
    cash = annual(con, t, "CashAndCashEquivalentsAtCarryingValue")
    con.close()

    if not rev or not ebit:
        raise SystemExit(f"{t}: missing revenue or EBIT in the facts table — run fetch_sec.py first")
    yr = max(rev)
    R, E = rev[yr], ebit[yr] / 1e3 if ebit[yr] > 1e7 else ebit[yr]
    # EDGAR values are in USD; normalise everything to USD m
    def m(d):  # noqa: E306
        return d.get(yr, 0.0) / 1e6
    R = rev[yr] / 1e6
    ebit_m, da_m, capex_m, cash_m = m(ebit), m(da), m(capex), m(cash)
    debt_m = (debt.get(yr, 0.0) / 1e6) if debt else 0.0
    interest_m = m(interest)

    tax_rate = (tax.get(yr, 0.0) / pbt[yr]) if pbt and pbt.get(yr) else 0.21
    tax_rate = min(max(tax_rate, 0.15), 0.30)

    price = last_price(Path(a.prices) / f"{t}.csv")
    sh = shares_outstanding(t)
    mcap = price * sh

    beta = a.beta if a.beta is not None else 1.0
    ke = a.rf + beta * a.erp
    kd = max(interest_m / debt_m if debt_m else 0.05, 0.04)
    w_e = mcap / (mcap + debt_m)
    w_d = 1 - w_e
    wacc = w_e * ke + w_d * kd * (1 - tax_rate)

    ebit_margin = ebit_m / R
    da_pct = da_m / R
    capex_pct = capex_m / R
    g_hist = min(max(cagr(rev), 0.02), 0.12)

    print(f"=== {t} · FY{yr} base year (USD m) ===")
    print(f"  revenue {R:,.0f} | EBIT {ebit_m:,.0f} ({ebit_margin:.1%}) | D&A {da_m:,.0f} ({da_pct:.1%})")
    print(f"  capex {capex_m:,.0f} ({capex_pct:.1%}) | debt {debt_m:,.0f} | cash {cash_m:,.0f} | tax {tax_rate:.1%}")
    print(f"  revenue CAGR (3y) {g_hist:.1%} | price {price:,.2f} | shares {sh:,.1f}m | mcap {mcap:,.0f}")

    print("\n=== WACC ===")
    print(f"  ke = {a.rf:.2%} + {beta:.3f} x {a.erp:.2%} = {ke:.2%}")
    print(f"  kd = {kd:.2%} (after tax {kd * (1 - tax_rate):.2%}) | weights E {w_e:.0%} / D {w_d:.0%}")
    print(f"  WACC = {wacc:.2%}")

    # ---- forecast ----
    rows, rev_t = [], R
    print(f"\n=== forecast ({a.years}y) ===")
    print("  year    revenue    EBIT   NOPAT    D&A   capex    dNWC    FCFF")
    for i in range(1, a.years + 1):
        growth = g_hist + (a.g - g_hist) * i / a.years          # linear fade to terminal growth
        prev = rev_t
        rev_t = rev_t * (1 + growth)
        ebit_t = rev_t * ebit_margin
        nopat = ebit_t * (1 - tax_rate)
        da_t = rev_t * da_pct
        capex_t = rev_t * capex_pct
        dnwc = (rev_t - prev) * a.nwc
        fcff = nopat + da_t - capex_t - dnwc
        rows.append((yr + i, rev_t, ebit_t, nopat, da_t, capex_t, dnwc, fcff))
        print(f"  {yr+i}E {rev_t:9,.0f} {ebit_t:7,.0f} {nopat:7,.0f} {da_t:6,.0f} {capex_t:7,.0f} "
              f"{dnwc:7,.0f} {fcff:7,.0f}")

    def value(wacc_r: float, g_r: float) -> tuple[float, float, float]:
        pv = sum(r[7] / (1 + wacc_r) ** i for i, r in enumerate(rows, start=1))
        tv = rows[-1][7] * (1 + g_r) / (wacc_r - g_r)
        pv_tv = tv / (1 + wacc_r) ** a.years
        ev = pv + pv_tv
        equity = ev - debt_m + cash_m
        return ev, equity, equity / sh

    ev, equity, fv = value(wacc, a.g)
    print(f"\n=== bridge ===")
    print(f"  PV of forecast FCFF  {sum(r[7]/(1+wacc)**i for i,r in enumerate(rows,start=1)):>10,.0f}")
    print(f"  PV of terminal value {ev - sum(r[7]/(1+wacc)**i for i,r in enumerate(rows,start=1)):>10,.0f} "
          f"({(ev - sum(r[7]/(1+wacc)**i for i,r in enumerate(rows,start=1)))/ev:.0%} of EV)")
    print(f"  EV {ev:,.0f} - debt {debt_m:,.0f} + cash {cash_m:,.0f} = equity {equity:,.0f}")
    print(f"  fair value ${fv:,.2f}/share vs market ${price:,.2f} ({fv/price-1:+.0%})")

    # ---- reverse DCF: what perpetual growth does the market price imply? ----
    equity_mkt = mcap
    ev_mkt = equity_mkt + debt_m - cash_m
    pv_explicit = sum(r[7] / (1 + wacc) ** i for i, r in enumerate(rows, start=1))
    need_tv_pv = ev_mkt - pv_explicit
    if need_tv_pv > 0:
        tv_needed = need_tv_pv * (1 + wacc) ** a.years
        fcff_last = rows[-1][7]
        # tv = fcff*(1+g)/(wacc-g)  ->  g = (tv*wacc - fcff) / (tv + fcff)
        g_implied = (tv_needed * wacc - fcff_last) / (tv_needed + fcff_last)
        print(f"\n=== reverse DCF (what the market assumes) ===")
        print(f"  market EV {ev_mkt:,.0f} vs modelled EV {ev:,.0f}")
        print(f"  terminal growth implied by the market: {g_implied:.2%} "
              f"(model uses {a.g:.2%}, nominal GDP is typically ~4%)")
        if g_implied > 0.06:
            print("  -> above any sustainable perpetual rate: the market is pricing growth this model "
                  "does not assume. Either believe the growth story or the shares are expensive.")

    print("\n=== sensitivity: fair value $/share (WACC x terminal g) ===")
    for dw in (-0.02, -0.01, 0.0, 0.01, 0.02):
        cells = []
        for g in (0.015, 0.025, 0.035):
            _, _, v = value(wacc + dw, g)
            cells.append(f"g{g:.1%} {v:7.2f}")
        print(f"  WACC {wacc+dw:.2%}  " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
