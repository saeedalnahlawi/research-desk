#!/usr/bin/env python3
"""Run sql/queries.sql against the SQLite database and print the result sets.

The sqlite3 command-line tool is not installed everywhere; this runner only needs
the standard library. Dot-commands (.headers/.mode) are skipped.

  python3 scripts/run_queries.py                    # all statements
  python3 scripts/run_queries.py --only Q5          # just one block
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path


def split_statements(sql: str) -> list[tuple[str, str]]:
    """Return (label, statement) pairs. A label is the leading '-- Qn.' comment."""
    blocks, label, buf = [], "query", []
    for line in sql.splitlines():
        m = re.match(r"--\s*(Q\d+)\.", line)
        if m:
            if any(l.strip() and not l.strip().startswith("--") for l in buf):
                blocks.append((label, "\n".join(buf)))
            label, buf = m.group(1), []
            continue
        if line.strip().startswith("."):
            continue
        buf.append(line)
    if any(l.strip() and not l.strip().startswith("--") for l in buf):
        blocks.append((label, "\n".join(buf)))
    return [(l, s.strip().rstrip(";")) for l, s in blocks if s.strip()]


def show(con: sqlite3.Connection, label: str, stmt: str, width: int = 22) -> None:
    cur = con.execute(stmt)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"\n### {label}  ({len(rows)} rows)")
    print(" | ".join(c[:width].ljust(min(width, len(c))) for c in cols))
    for r in rows[:12]:
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append(f"{v:,.1f}")
            else:
                cells.append(str(v)[:width])
        print(" | ".join(cells))
    if len(rows) > 12:
        print(f"... {len(rows) - 12} more rows")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/research.db")
    ap.add_argument("--sql", default="sql/queries.sql")
    ap.add_argument("--only")
    a = ap.parse_args()

    db, sqlf = Path(a.db), Path(a.sql)
    for p in (db, sqlf):
        if not p.is_file():
            print(f"missing {p}", file=sys.stderr)
            return 2

    con = sqlite3.connect(db)
    for label, stmt in split_statements(sqlf.read_text()):
        if a.only and label != a.only:
            continue
        show(con, label, stmt)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
