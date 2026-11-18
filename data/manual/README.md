# Manual data — Arab Bank

Why by hand: there is no free, machine-readable feed for Amman Stock Exchange filings. Typing the
numbers yourself is not busywork — it forces you to read the statements and to notice how a bank's
income statement is built differently from an industrial's.

## What to collect

`arabbank_figures.csv` — three years, twelve items. Leave `value` empty until you have read the number
off the page, then fill `source_page` so anyone can check you.

## Where the numbers live

1. **Investor relations** section of the bank's own website — annual report PDF (audited financial
   statements are the last ~40 pages).
2. **ASE / Jordan Securities Commission disclosure portal** — the same audited statements, plus quarterly
   disclosures.
3. For the market comparison (P/B, P/E) you also need: **share price** on a chosen date and **shares
   outstanding**. Add them as two extra rows — `item = share_price` (unit JOD) and `item = shares_outstanding`
   (unit millions).

## Bank-specific definitions — get these exactly right

| Item | Definition | Where |
|---|---|---|
| Net interest income | Interest income − interest expense | Income statement |
| Non-interest income | Fees, commissions, FX, investment gains | Income statement |
| Operating expenses | Staff + admin + depreciation | Income statement |
| Impairment provisions | Credit loss charge for the year | Income statement |
| Gross loans | Before provisions | Balance sheet / credit note |
| Customer deposits | Exclude bank deposits and borrowed funds | Balance sheet |
| NPL ratio | Non-performing loans ÷ gross loans | Credit quality note |
| NPL coverage | Provisions held ÷ NPLs | Credit quality note |
| CAR | Total capital ÷ risk-weighted assets | Capital adequacy note |

## The trap that matters

A bank's "revenue" is net interest income plus non-interest income. Do **not** compute a gross margin,
and do not use EV/EBITDA — a bank's debt is its inventory. The two questions a bank valuation answers are:
*what return on equity does it earn, and what is that ROE worth relative to book?*

## Interim periods — the comparability trap

Flow items (profit, interest income, expenses) cover six months in an H1 column; balance-sheet items
(assets, loans, deposits, equity) are a single-day snapshot. So:

- **Annualise flows, never stocks.** `bank_ratios` multiplies interim ROE by 2 and leaves NIM, cost/income
  and every balance-sheet ratio unscaled. Do not "fix" that.
- **Never annualise equity, assets or loans** — they are a point in time, and doubling them is a factual error.
- NPL ratio and coverage need no adjustment; they are ratios of two stocks.
- When you write the note, say which column is annualised and which is not. A reader who spots an
  inconsistency you didn't disclose stops trusting the rest of the table.

## Step order

1. Fill the CSV for the three periods agreed: **FY 2024, FY 2025, H1 2026** (14 items each, 42 cells).
2. Load it: `python3 scripts/load_manual.py` (build once you have the data).
3. Run `sql/bank_queries.sql` — NIM, cost-to-income, ROE, leverage, and the P/B-vs-ROE comparison.
4. Only then open a DCF — and expect it to be the *wrong* tool, which is the lesson.
