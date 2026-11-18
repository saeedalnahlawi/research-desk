# Equity Research Desk

Personal equity research: clean financial data → SQL → valuation → published notes.

Reproducible rather than asserted. Every number in a note traces back to a script in this repository, and to a
page in a filing. Coverage spans **US-listed companies (SEC EDGAR)**, **Amman Stock Exchange** filers and
**GCC** operators — with the valuation method chosen by sector, not by exchange.

## Coverage and how each part works

| Market | Data source | Script |
|---|---|---|
| US-listed (NYSE, NASDAQ) | SEC EDGAR XBRL company facts — free, no key | `scripts/fetch_sec.py` |
| Amman Stock Exchange | Audited statements entered by hand, with page references | `data/manual/`, `scripts/load_manual.py` |
| GCC telecoms & banks | Same: filings first, peer multiples from a dated source | `profiles/`, `reviews/` |
| Prices and beta | Nasdaq quote API for US names; ASE/WSJ for Jordanian names | `scripts/fetch_prices.py`, `estimate_beta.py` |

## Valuation engines

| Engine | Used for | Why not a DCF |
|---|---|---|
| `scripts/value_bank.py` | Banks | Interest expense is an operating cost; debt is raw material. Residual income, P/B vs ROE |
| `scripts/value_telecom.py` | Telecoms | Capex intensity decides the answer, so it gets modelled and sensitised explicitly |
| `scripts/value_dcf.py` | Industrials, consumer, tech | FCFF DCF with a WACC built from the Treasury curve and a regression beta |

Each engine prints a **reverse DCF** (what the market price implies about growth or risk) and a **plausibility
gate** that refuses to present a result when the inputs cannot support it.

## What is here

| Folder | Contents |
|---|---|
| `scripts/fetch_sec.py` | US-listed financials from EDGAR into tidy CSVs |
| `scripts/load_sqlite.py` | Loads CSVs into SQLite; builds the `annual` and `revenue_annual` views |
| `sql/queries.sql` | Ratio and year-over-year queries, including window functions |
| `scripts/run_queries.py` | Runs the SQL through Python's sqlite3 — no CLI needed |
| `sql/bank_queries.sql` | Bank ratios (ROE, NIM, cost/income, NPL), P/B vs P/E, implied-ROE identity |
| `scripts/value_*.py` | The three valuation engines above |
| `scripts/profile_from_edgar.py` | Builds a valuation profile from EDGAR facts, reporting anything it cannot tag |
| `profiles/` | Every assumption for a company in one readable file (`jtel.json`, `t.json`) |
| `data/manual/` | Hand-entered figures with page references (Arab Bank FY2024–H1 2026) |
| `notes/` | Published and draft research notes, one markdown file per company |
| `reviews/` | Model critiques and source verification — including the corrections |
| `docs/how-i-work.md` | Method, standards and limitations — read this first |
| `docs/methods-by-sector.md` | Which method applies to which sector, and what changes for US filers |
| `journal/` | Trading journal template (paper trading), kept separate from the analysis |

Generated data (`data/raw`, `data/source`, `*.db`) is git-ignored.

## Run it

```bash
python3 scripts/fetch_sec.py --tickers AAPL KO     # US filers, ~4k rows, about 5 seconds
python3 scripts/load_sqlite.py                     # CSV -> data/research.db
python3 scripts/run_queries.py                     # all five query blocks
python3 scripts/run_queries.py --only Q5           # just the window-function one
python3 scripts/value_telecom.py --profile profiles/jtel.json
```

Requires Python 3.9+ and nothing else. No pandas, no SQL install — `sqlite3` ships with Python.

## Sample output (verified, Nov 2026 data)

```
### Q4   latest fiscal year: net margin, ROE, leverage
ticker | fiscal_year_end | net_margin_pct | roe_pct | liabilities_to_equity
AAPL   | 2026-09-26      | 27.6           | 117.9   | 2.6
KO     | 2025-12-31      | 27.3           | 40.7    | NULL
```

`KO` leverage is `NULL`, not broken: Coca-Cola tags liabilities under a different us-gaap concept than Apple
does, so the join finds nothing. **That is the actual work** — reported data is inconsistent across companies and
the analyst has to decide how to handle it rather than quietly dropping the row.

## Method notes

- Annual figures only: full-year income-statement facts (~365 days) and instant balance-sheet facts, as
  reported on form 10-K.
- Revenue is resolved with `COALESCE` across the two us-gaap revenue concepts; other filers may need a third.
- Currencies are never mixed: a JOD price against USD book value is a 40% error that looks plausible, so the
  bank model refuses to compute a multiple without an FX rate.
- This repository is analysis, not advice. Nothing here is a recommendation to buy or sell.

## Where it is going

Built in public, one sector at a time. The method is fixed (`docs/how-i-work.md`); the coverage grows. Next: a
telecom note from `scripts/value_telecom.py`, then an industrial so the portfolio is not two banks and a phone
company — then the same pipeline applied to NYSE/NASDAQ names where EDGAR does the data work automatically.
