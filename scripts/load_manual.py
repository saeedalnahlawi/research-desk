#!/usr/bin/env python3
"""Load manually-entered figures (banks, ASE companies) into the research DB.

The CSV is filled by hand from annual reports: year,item,value,unit,source_page,note.
Empty `value` cells are skipped and reported, so a half-finished CSV still loads.

  python3 scripts/load_manual.py --csv data/manual/arabbank_figures.csv --db data/research.db
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

SCHEMA = """
DROP TABLE IF EXISTS manual_figures;
CREATE TABLE manual_figures (
    entity      TEXT NOT NULL,
    year        INTEGER NOT NULL,
    item        TEXT NOT NULL,
    value       REAL,
    unit        TEXT,
    source_page TEXT,
    note        TEXT
);
CREATE INDEX idx_manual ON manual_figures (entity, item, year);

-- One row per year with the bank metrics that actually matter.
DROP VIEW IF EXISTS bank_ratios;
CREATE VIEW bank_ratios AS
SELECT entity, year,
       ROUND(MAX(CASE WHEN item = 'net_profit' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_equity' THEN value END), 0) * 100, 1) AS roe_pct,
       ROUND((MAX(CASE WHEN item = 'net_interest_income' THEN value END)
              + MAX(CASE WHEN item = 'non_interest_income' THEN value END))
             / NULLIF(MAX(CASE WHEN item = 'operating_expenses' THEN value END), 0), 2)          AS income_to_cost_x,
       ROUND(MAX(CASE WHEN item = 'net_interest_income' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100, 2)          AS nim_on_assets_pct,
       ROUND(MAX(CASE WHEN item = 'customer_deposits' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) * 100, 1)          AS deposits_to_assets_pct,
       ROUND(MAX(CASE WHEN item = 'gross_loans' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'customer_deposits' THEN value END), 0) * 100, 1)     AS loans_to_deposits_pct,
       ROUND(MAX(CASE WHEN item = 'non_performing_loans' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'gross_loans' THEN value END), 0) * 100, 2)           AS npl_ratio_pct,
       MAX(CASE WHEN item = 'npl_coverage' THEN value END)                                       AS npl_coverage_pct,
       MAX(CASE WHEN item = 'capital_adequacy' THEN value END)                                   AS car_pct
FROM manual_figures
GROUP BY entity, year;
"""

# Item names are normalised so the CSV can be written by a human.
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


def entity_from(path: Path) -> str:
    return path.stem.replace("_figures", "").replace("_", " ").title()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/manual/arabbank_figures.csv")
    ap.add_argument("--db", default="data/research.db")
    a = ap.parse_args()

    src, db = Path(a.csv), Path(a.db)
    if not src.is_file():
        raise SystemExit(f"missing {src}")
    entity = entity_from(src)

    rows, empty = [], 0
    with src.open() as fh:
        for r in csv.DictReader(fh):
            raw = (r.get("value") or "").strip()
            if not raw:
                empty += 1
                continue
            try:
                v = float(raw.replace(",", ""))
            except ValueError:
                empty += 1
                continue
            item = ALIASES.get((r.get("item") or "").strip().lower(), (r.get("item") or "").strip().lower().replace(" ", "_"))
            rows.append((entity, int(r["year"]), item, v, r.get("unit", ""), r.get("source_page", ""), r.get("note", "")))

    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO manual_figures VALUES (?,?,?,?,?,?,?)", rows)
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM bank_ratios").fetchone()[0]
    con.close()

    print(f"{entity}: loaded {len(rows)} values, {empty} cells still empty, {n} year-rows in bank_ratios")
    if not rows:
        print("nothing to load yet — fill data/manual/README.md step 1 first", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
