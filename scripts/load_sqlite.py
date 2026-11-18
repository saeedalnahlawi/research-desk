#!/usr/bin/env python3
"""Load the tidy EDGAR CSVs into a SQLite database.

  python3 scripts/load_sqlite.py --raw data/raw --db data/research.db
  sqlite3 data/research.db < sql/queries.sql
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

SCHEMA = """
DROP TABLE IF EXISTS facts;
CREATE TABLE facts (
    ticker   TEXT NOT NULL,
    concept  TEXT NOT NULL,
    unit     TEXT,
    start    TEXT,
    end      TEXT,
    value    REAL,
    fy       TEXT,
    fp       TEXT,
    form     TEXT,
    filed    TEXT,
    frame    TEXT
);
CREATE INDEX idx_facts_ticker_concept ON facts (ticker, concept, end);

-- Annual figures only: full-year duration facts, one row per fiscal year.
DROP VIEW IF EXISTS annual;
CREATE VIEW annual AS
SELECT ticker, concept, end, MAX(value) AS value, MAX(fy) AS fy
FROM facts
WHERE form = '10-K'
  AND (
        (start IS NULL OR start = '')                       -- balance-sheet items: instant facts
        OR julianday(end) - julianday(start) > 300          -- income items: ~12 months, no quarters
      )
GROUP BY ticker, concept, end;

-- One clean revenue series per company per year: companies tag revenue under
-- two different us-gaap concepts, so COALESCE picks whichever exists.
DROP VIEW IF EXISTS revenue_annual;
CREATE VIEW revenue_annual AS
SELECT ticker, end,
       COALESCE(MAX(CASE WHEN concept = 'Revenues' THEN value END),
                MAX(CASE WHEN concept = 'RevenueFromContractWithCustomerExcludingAssessedTax'
                         THEN value END)) AS revenue
FROM annual
WHERE concept IN ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax')
GROUP BY ticker, end;

-- Latest annual value per concept, for quick screening.
DROP VIEW IF EXISTS latest_annual;
CREATE VIEW latest_annual AS
SELECT a.ticker, a.concept, a.value, a.end
FROM annual a
JOIN (SELECT ticker, concept, MAX(end) AS end FROM annual GROUP BY ticker, concept) m
  ON a.ticker = m.ticker AND a.concept = m.concept AND a.end = m.end;
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--db", default="data/research.db")
    a = ap.parse_args()

    raw = Path(a.raw)
    files = sorted(raw.glob("*_facts.csv"))
    if not files:
        raise SystemExit(f"no CSVs in {raw} — run scripts/fetch_sec.py first")

    db = Path(a.db)
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)

    total = 0
    for f in files:
        with f.open() as fh:
            rows = list(csv.DictReader(fh))
        con.executemany(
            "INSERT INTO facts VALUES (:ticker,:concept,:unit,:start,:end,:value,:fy,:fp,:form,:filed,:frame)",
            [{**r, "value": float(r["value"]) if r.get("value") not in (None, "") else None} for r in rows])
        total += len(rows)
        print(f"loaded {f.name}: {len(rows)} rows")
    con.commit()
    n_annual = con.execute("SELECT COUNT(*) FROM annual").fetchone()[0]
    print(f"facts={total}  annual_rows={n_annual}  db={db}")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
