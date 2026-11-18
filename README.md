# ASE Research Desk

Personal equity research: clean financial data → SQL → valuation → published notes.

Built while job-hunting as a finance graduate, to make the analysis reproducible rather than
asserted. Every number in a published note traces back to a script in this repository.

## What is here

| Folder | Contents |
|---|---|
| `scripts/fetch_sec.py` | Pulls US-listed company financials from SEC EDGAR (free, no key) into tidy CSVs |
| `scripts/load_sqlite.py` | Loads the CSVs into SQLite and builds the `annual` / `revenue_annual` views |
| `sql/queries.sql` | The practice set: revenue series, ratios, year-over-year growth with window functions |
| `scripts/run_queries.py` | Runs `sql/queries.sql` and prints the result sets (stdlib only, no `sqlite3` CLI needed) |
| `notes/` | Published research notes, one markdown file per company |
| `data/manual/` | Hand-entered bank figures (Arab Bank: FY2024, FY2025, H1 2026) + the definitions that matter |
| `sql/bank_queries.sql` | Bank ratios (ROE, NIM, cost/income, NPL), P/B vs P/E, and the implied-ROE identity |
| `scripts/value_bank.py` | Residual-income valuation for banks, with sensitivity grid (ARBK) |
| `scripts/value_dcf.py` | FCFF DCF for non-financials: EDGAR → forecast → WACC → EV → per share, plus reverse DCF |
| `scripts/fetch_prices.py` / `estimate_beta.py` | Daily closes (Nasdaq API) and beta by regression vs SPY |
| `notes/` | Valuation notes: `arabbank-valuation.md`, `dcf-engine-demo.md` |
| `docs/methods-by-sector.md` | Which method applies to which sector, and what changes for US filers |
| `journal/` | Trading journal template (paper trading) — kept separate from the analysis |
| `data/` | Generated. Not committed. |

## Run it

```bash
python3 scripts/fetch_sec.py --tickers AAPL KO     # ~4k rows, about 5 seconds
python3 scripts/load_sqlite.py                     # CSV -> data/research.db
python3 scripts/run_queries.py                     # all five query blocks
python3 scripts/run_queries.py --only Q5           # just the window-function one
```

Requires Python 3.9+ and nothing else. No pandas, no SQL install — `sqlite3` ships with Python.

## Sample output (verified, Nov 2026 data)

```
### Q4   latest fiscal year: net margin, ROE, leverage
ticker | fiscal_year_end | net_margin_pct | roe_pct | liabilities_to_equity
AAPL   | 2026-09-26      | 27.6           | 117.9   | 2.6
KO     | 2025-12-31      | 27.3           | 40.7    | NULL
```

`KO` leverage is `NULL`, not broken: Coca-Cola tags liabilities under a different us-gaap concept
than Apple does, so the join finds nothing. **That is the actual work** — the first thing every
analyst learns is that reported data is inconsistent across companies and you must decide how to
handle it rather than quietly dropping the row.

## Method notes

- Annual figures only: full-year income-statement facts (~365 days) and instant balance-sheet facts
  as reported on form 10-K.
- Revenue is resolved with `COALESCE` across the two us-gaap revenue concepts; other companies may
  need a third.
- This repository is analysis, not advice. Nothing here is a recommendation to buy or sell.

## Roadmap

See `../../roadmap.md` in the parent workspace: 16 weeks, W01 starting 22 Nov 2026.
Gate 1 (Week 4): this repo reproduces a ratio table for three companies from one command.
