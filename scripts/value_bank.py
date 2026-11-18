#!/usr/bin/env python3
"""Excess-return (residual income) valuation for a bank, with sensitivity grid.

Method: Value = Book_0 + PV(excess returns over 5 years) + PV(terminal excess return, growing at g).
Bank-specific because FCFF/EV has no meaning when interest expense is operating cost.

  python3 scripts/value_bank.py
  python3 scripts/value_bank.py --coe 0.11 --g 0.04 --scenario base

Every input traces to data/manual/arabbank_figures.csv (see SOURCES.md for pages).
"""
from __future__ import annotations

import argparse

# ---- Inputs (USD m unless noted) — from the filings -------------------------------
BOOK_0 = 13531.795      # total equity, 30 Jun 2026
SHARES = 640.8          # millions of shares
FX_JOD_PER_USD = 0.708  # CBJ official (USD = 708 fils)
PRICE_JOD = 7.47        # ASE close 18 Nov 2026
INCOME_2025 = 3586.023
OPEX_2025 = 861.424 + 567.389 + 145.073
ECL_2025 = 423.153
PROFIT_2025 = 1130.356
PBT_2025 = 1555.249
TAX_RATE = (PBT_2025 - PROFIT_2025) / PBT_2025        # 27.3% implied

SCENARIOS = {
    "bear": dict(growth=[0.020] * 5, eff=[0.445, 0.450, 0.455, 0.458, 0.460], ecl=0.135, payout=0.40),
    "base": dict(growth=[0.040, 0.038, 0.036, 0.035, 0.035],
                 eff=[0.437, 0.440, 0.442, 0.444, 0.445], ecl=0.120, payout=0.40),
    "bull": dict(growth=[0.055, 0.050, 0.048, 0.045, 0.045],
                 eff=[0.430, 0.425, 0.420, 0.415, 0.410], ecl=0.100, payout=0.45),
}


def forecast(s: dict) -> tuple[list[dict], float]:
    inc, book, rows = INCOME_2025, BOOK_0, []
    for t in range(5):
        inc *= 1 + s["growth"][t]
        opex = inc * s["eff"][t]
        ecl = inc * s["ecl"]
        profit = (inc - opex - ecl) * (1 - TAX_RATE)
        rows.append(dict(year=2026 + t, income=inc, opex=opex, ecl=ecl, profit=profit,
                         roe=profit / book, book_open=book))
        book += profit * (1 - s["payout"])
    return rows, book


def value(rows: list[dict], book_end: float, coe: float, g: float) -> float:
    pv = sum((r["roe"] - coe) * r["book_open"] / (1 + coe) ** (i + 1) for i, r in enumerate(rows))
    excess_terminal = (rows[-1]["roe"] - coe) * book_end
    tv = excess_terminal / (coe - g) / (1 + coe) ** len(rows)
    return BOOK_0 + pv + tv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coe", type=float, default=0.11)
    ap.add_argument("--g", type=float, default=0.04)
    ap.add_argument("--scenario", default="base", choices=list(SCENARIOS))
    a = ap.parse_args()

    bvps_jod = BOOK_0 / SHARES * FX_JOD_PER_USD
    print(f"book per share JOD {bvps_jod:.2f} | price JOD {PRICE_JOD:.2f} | P/B {PRICE_JOD / bvps_jod:.2f}")
    print(f"implied tax rate {TAX_RATE:.1%} | FY2025 efficiency {OPEX_2025 / INCOME_2025:.1%} | "
          f"ECL/income FY2025 {ECL_2025 / INCOME_2025:.1%}\n")

    rows, book_end = forecast(SCENARIOS[a.scenario])
    print(f"--- {a.scenario} case, COE {a.coe:.0%}, g {a.g:.0%} ---")
    for r in rows:
        print(f"  {r['year']}E income {r['income']:>7,.0f}  opex {r['opex']:>6,.0f}  ecl {r['ecl']:>5,.0f}  "
              f"profit {r['profit']:>6,.0f}  ROE {r['roe']:.2%}")
    v = value(rows, book_end, a.coe, a.g)
    fv = v / SHARES * FX_JOD_PER_USD
    print(f"  equity 2030E {book_end:,.0f} | value {v:,.0f} USD m | fair value JOD {fv:.2f} "
          f"({(fv / PRICE_JOD - 1) * 100:+.0f}% vs market)")
    print(f"  justified P/B at ROE {rows[-1]['roe']:.1%}: "
          f"{((rows[-1]['roe'] - a.g) / (a.coe - a.g)):.2f}x book = "
          f"JOD {((rows[-1]['roe'] - a.g) / (a.coe - a.g)) * bvps_jod:.2f}")

    print("\n--- sensitivity grid, fair value JOD ---")
    for coe in (0.10, 0.11, 0.12, 0.14, 0.16):
        cells = []
        for g in (0.03, 0.04):
            vals = []
            for name, s in SCENARIOS.items():
                rws, be = forecast(s)
                vals.append(f"{name} {value(rws, be, coe, g) / SHARES * FX_JOD_PER_USD:5.2f}")
            cells.append(f"g{g:.0%}: " + " ".join(vals))
        print(f"COE {coe:.0%}  " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
