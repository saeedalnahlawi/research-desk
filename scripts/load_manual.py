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
-- roe_pct is annualised for interim periods (x2 for H1) so it is comparable
-- with a full year; nim, cost/income and balance-sheet ratios need no scaling.
DROP VIEW IF EXISTS bank_ratios;
CREATE VIEW bank_ratios AS
SELECT entity, period, year, is_interim,
       ROUND(MAX(CASE WHEN item = 'net_profit' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_equity' THEN value END), 0) * 100
             * (CASE WHEN is_interim = 1 THEN 2 ELSE 1 END), 1)                                    AS roe_pct,
       ROUND((MAX(CASE WHEN item = 'net_interest_income' THEN value END)
              + MAX(CASE WHEN item = 'non_interest_income' THEN value END))
             / NULLIF(MAX(CASE WHEN item = 'operating_expenses' THEN value END), 0), 2)            AS income_to_cost_x,
       ROUND(MAX(CASE WHEN item = 'net_interest_income' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100, 2)            AS nim_on_assets_pct,
       ROUND(MAX(CASE WHEN item = 'customer_deposits' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100, 1)            AS deposits_to_assets_pct,
       ROUND(MAX(CASE WHEN item = 'gross_loans' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'customer_deposits' THEN value END), 0) * 100, 1)       AS loans_to_deposits_pct,
       ROUND(MAX(CASE WHEN item = 'non_performing_loans' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'gross_loans' THEN value END), 0) * 100, 2)             AS npl_ratio_pct,
       MAX(CASE WHEN item = 'npl_coverage' THEN value END)                                         AS npl_coverage_pct,
       MAX(CASE WHEN item = 'capital_adequacy' THEN value END)                                     AS car_pct
FROM manual_figures
GROUP BY entity, period, year, is_interim;

-- Market multiples, where a share price and share count were entered.
DROP VIEW IF EXISTS bank_multiples;
CREATE VIEW bank_multiples AS
WITH mkt AS (
    SELECT entity, period, year,
           MAX(CASE WHEN item = 'share_price' THEN value END)       AS price,
           MAX(CASE WHEN item = 'shares_outstanding' THEN value END) AS shares_m,
           MAX(CASE WHEN item = 'total_equity' THEN value END)       AS equity,
           MAX(CASE WHEN item = 'net_profit' THEN value END)         AS net_profit,
           MAX(is_interim)                                           AS is_interim
    FROM manual_figures GROUP BY entity, period, year
)
SELECT entity, period, year, is_interim, price, shares_m,
       ROUND(price * shares_m, 1)                                        AS market_cap_m,
       ROUND(price * shares_m / NULLIF(equity, 0), 2)                     AS pb_x,
       ROUND(price * shares_m
             / NULLIF(net_profit * (CASE WHEN is_interim = 1 THEN 2 ELSE 1 END), 0), 2) AS pe_x
FROM mkt
WHERE price IS NOT NULL AND shares_m IS NOT NULL;
"""

# Item names normalised so a human can write the CSV in plain language.
ALIASES = {
    "net interest income": "net_interest_income",
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
