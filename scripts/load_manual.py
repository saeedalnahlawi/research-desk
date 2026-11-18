#!/usr/bin/env python3
"""Load manually-entered figures (banks, ASE companies) into the research DB.

The CSV is filled by hand from filings: period,item,value,unit,source_page,note
where period is 'FY 2024', 'FY 2025' or an interim such as 'H1 2026'.

Empty `value` cells are skipped and reported, so a half-finished CSV still loads.

  python3 scripts/load_manual.py --csv data/manual/arabbank_figures.csv --db data/research.db
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from pathlib import Path

SCHEMA = """
DROP TABLE IF EXISTS manual_figures;
CREATE TABLE manual_figures (
    entity      TEXT NOT NULL,
    period      TEXT NOT NULL,          -- 'FY 2024', 'H1 2026'
    year        INTEGER NOT NULL,       -- 2024, 2026 (sort key)
    is_interim  INTEGER NOT NULL,       -- 1 for H1/9M, 0 for full year
    item        TEXT NOT NULL,
    value       REAL,
    unit        TEXT,
    source_page TEXT,
    note        TEXT
);
CREATE INDEX idx_manual ON manual_figures (entity, item, year);

-- One row per period with the bank metrics that matter.
-- Flow ratios (ROE, NIM) are annualised for interim periods (x2 for H1) so they compare
-- with a full year; stock ratios and ratios of two flows are not scaled.
DROP VIEW IF EXISTS bank_ratios;
CREATE VIEW bank_ratios AS
SELECT entity, period, year, is_interim,
       ROUND(MAX(CASE WHEN item = 'profit' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_equity' THEN value END), 0) * 100
             * (CASE WHEN is_interim = 1 THEN 2 ELSE 1 END), 2)                                   AS roe_pct,
       ROUND(MAX(CASE WHEN item = 'net_interest_income' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100
             * (CASE WHEN is_interim = 1 THEN 2 ELSE 1 END), 2)                                   AS nim_on_assets_pct,
       ROUND((MAX(CASE WHEN item = 'employees_expenses' THEN value END)
              + MAX(CASE WHEN item = 'other_expenses' THEN value END)
              + MAX(CASE WHEN item = 'depreciation' THEN value END))
             / NULLIF(MAX(CASE WHEN item = 'total_income' THEN value END), 0) * 100, 1)           AS efficiency_ratio_pct,
       ROUND(MAX(CASE WHEN item = 'total_expenses' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_income' THEN value END), 0) * 100, 1)           AS cost_incl_ecl_pct,
       ROUND(MAX(CASE WHEN item = 'dcf_net' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'customer_deposits' THEN value END), 0) * 100, 1)      AS loans_to_deposits_pct,
       ROUND(MAX(CASE WHEN item = 'total_equity' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100, 2)           AS equity_to_assets_pct,
       MAX(CASE WHEN item = 'npl_ratio' THEN value END)                                           AS npl_ratio_pct,
       MAX(CASE WHEN item = 'car' THEN value END)                                                 AS car_pct,
       MAX(CASE WHEN item = 'npl' THEN value END)                                                 AS npl_usd_m
FROM manual_figures
GROUP BY entity, period, year, is_interim;

-- Market multiples. Currency trap: Arab Bank shares trade in JOD on the ASE while the
-- statements are in USD, so a JOD/USD rate is required; without it P/B would be nonsense.
-- The view returns no rows until price, share count and FX rate are all entered.
DROP VIEW IF EXISTS bank_multiples;
CREATE VIEW bank_multiples AS
WITH m AS (
    SELECT entity, period, year, MAX(is_interim) AS is_interim,
           MAX(CASE WHEN item = 'share_price' THEN value END) AS price_jod,
           MAX(CASE WHEN item = 'shares'      THEN value END) AS shares_m,
           MAX(CASE WHEN item = 'fx_jod_usd'  THEN value END) AS fx,
           MAX(CASE WHEN item = 'total_equity' THEN value END) AS equity_usd_m,
           MAX(CASE WHEN item = 'profit'       THEN value END) AS profit_usd_m
    FROM manual_figures GROUP BY entity, period, year
)
SELECT entity, period, year, is_interim, price_jod, shares_m, fx,
       ROUND(price_jod * shares_m, 1)                                          AS market_cap_jod_m,
       ROUND(price_jod * shares_m / NULLIF(fx, 0), 1)                          AS market_cap_usd_m,
       ROUND(price_jod * shares_m / NULLIF(fx, 0) / NULLIF(equity_usd_m, 0), 2) AS pb_x,
       ROUND(price_jod * shares_m / NULLIF(fx, 0)
             / NULLIF(profit_usd_m * (CASE WHEN is_interim = 1 THEN 2 ELSE 1 END), 0), 2) AS pe_x
FROM m
WHERE price_jod IS NOT NULL AND shares_m IS NOT NULL AND fx IS NOT NULL;
"""

# Item names normalised so a human can write the CSV in plain language.
ALIASES = {
    "interest income": "interest_income",
    "interest expense": "interest_expense",
    "net interest income": "net_interest_income",
    "net commission income": "net_commission_income",
    "non-interest income": "non_interest_income",
    "total income": "total_income",
    "employees expenses": "employees_expenses",
    "employees' expenses": "employees_expenses",
    "other expenses": "other_expenses",
    "depreciation and amortization": "depreciation",
    "provision for impairment ecl": "ecl",
    "expected credit loss on financial assets": "ecl",
    "impairment provisions": "impairment_provisions",
    "total expenses": "total_expenses",
    "operating expenses": "operating_expenses",
    "profit for the year": "profit",
    "profit for the period": "profit",
    "net profit": "net_profit",
    "total assets": "total_assets",
    "direct credit facilities net": "dcf_net",
    "gross loans and advances": "gross_loans",
    "customer deposits": "customer_deposits",
    "total equity": "total_equity",
    "non-performing loans": "npl",
    "non-performing loans (npl)": "npl",
    "npl ratio": "npl_ratio",
    "npl coverage ratio": "npl_coverage",
    "capital adequacy ratio": "car",
    "capital adequacy ratio (car)": "car",
    "shares outstanding": "shares",
    "fx rate (jod per usd)": "fx_jod_usd",
    "fx rate": "fx_jod_usd",
    "share price": "share_price",
    "non-interest income": "non_interest_income",
    "operating expenses": "operating_expenses",
    "impairment provisions": "impairment_provisions",
    "net profit": "net_profit",
    "total assets": "total_assets",
    "gross loans and advances": "gross_loans",
    "customer deposits": "customer_deposits",
    "total equity": "total_equity",
    "non-performing loans (npl)": "non_performing_loans",
    "npl coverage ratio": "npl_coverage",
    "capital adequacy ratio (car)": "capital_adequacy",
    "share price": "share_price",
    "shares outstanding": "shares_outstanding",
}

PERIOD_RE = re.compile(r"(FY|H1|9M|Q1|Q2|Q3|Q4)\s*(\d{4})", re.I)


def entity_from(path: Path) -> str:
    return path.stem.replace("_figures", "").replace("_", " ").title()


def parse_period(text: str) -> tuple[str, int, int] | None:
    m = PERIOD_RE.search((text or "").strip())
    if not m:
        return None
    label = m.group(1).upper()
    year = int(m.group(2))
    return (f"{label} {year}", year, 0 if label == "FY" else 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/manual/arabbank_figures.csv")
    ap.add_argument("--db", default="data/research.db")
    a = ap.parse_args()

    src, db = Path(a.csv), Path(a.db)
    if not src.is_file():
        raise SystemExit(f"missing {src}")
    entity = entity_from(src)

    rows, empty, bad_period = [], 0, set()
    with src.open() as fh:
        for r in csv.DictReader(fh):
            p = parse_period(r.get("period") or r.get("year") or "")
            if not p:
                bad_period.add((r.get("period") or "") or "(blank)")
                continue
            raw = (r.get("value") or "").strip()
            if not raw:
                empty += 1
                continue
            try:
                v = float(raw.replace(",", ""))
            except ValueError:
                empty += 1
                continue
            item_raw = (r.get("item") or "").strip()
            item = ALIASES.get(item_raw.lower(), item_raw.lower().replace(" ", "_"))
            rows.append((entity, p[0], p[1], p[2], item, v,
                         r.get("unit", ""), r.get("source_page", ""), r.get("note", "")))

    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO manual_figures VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    n_ratio = con.execute("SELECT COUNT(*) FROM bank_ratios").fetchone()[0]
    n_mult = con.execute("SELECT COUNT(*) FROM bank_multiples").fetchone()[0]
    con.close()

    print(f"{entity}: loaded {len(rows)} values, {empty} empty cells, "
          f"{n_ratio} period rows in bank_ratios, {n_mult} with multiples")
    if bad_period:
        print(f"unparsed periods (expected 'FY 2024' or 'H1 2026'): {sorted(bad_period)}")
    if not rows:
        print("nothing to load yet — fill the CSV from the annual report first")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())