# DCF engine — how it works and what it says about AAPL and KO

_19 Nov 2026. Second valuation engine in the repo, for non-financial companies. Banks still use
`scripts/value_bank.py`._

## What it does, in order

1. **Pull fundamentals from EDGAR** (`data/research.db`): revenue, EBIT, D&A, capex, tax, PBT, interest,
   long-term debt, cash — all annual, from the `annual` and `revenue_annual` views.
2. **Estimate beta by regression** (`scripts/estimate_beta.py`) against SPY, five years of daily returns,
   with R² reported so a weak beta is visible rather than hidden.
3. **Build WACC**: `ke = rf + beta × ERP` with the risk-free from the US Treasury curve (FRED DGS10, 5.12%
   at the time of writing), ERP 4.5%, `kd` from interest expense ÷ debt with a 4% floor, market-value weights.
4. **Forecast FCFF for five years**: revenue growth fades linearly from the three-year historical CAGR to the
   terminal rate; EBIT margin, D&A and capex held at the latest reported percentages of revenue; working
   capital at 3% of the revenue change; tax at the implied rate, clamped to 15–30%.
5. **Discount**: `EV = PV(FCFF) + PV(terminal)`, then `equity = EV − debt + cash`, then per share.
6. **Reverse DCF**: solve for the terminal growth the market price implies, given the same WACC and forecast.
7. **Sensitivity grid**: fair value across WACC ±2pp and terminal growth 1.5–3.5%.

## Results (market prices 17 Nov 2026)

| | AAPL | KO |
|---|---|---|
| Beta (5y daily vs SPY) | 1.144 (R² 0.50) | 0.235 (R² 0.06 — weak) |
| WACC | 10.16% | 7.82% |
| Fair value | $133.68 | $49.10 |
| Market price | $351.91 | $98.79 |
| Terminal value share of EV | 70% | 78% |
| **Terminal growth the market implies** | **7.70%** | **5.51%** |

## How to read that honestly

The engine does **not** say Apple is 62% overvalued. It says: *under a single-stage perpetuity at 2.5% growth
and a 10.2% cost of capital, these cash flows are worth about a third of the market price* — and then the
reverse DCF tells you why: the market is discounting **7.7% perpetual growth for Apple and 5.5% for Coca-Cola**,
against a model assumption of 2.5% and a nominal-GDP anchor near 4%.

That is a real question for a note, not a verdict. To believe the market you must believe Apple compounds
above nominal GDP forever, which is a strong claim; to believe the model you must accept that a single-stage
terminal value badly understates a business still growing in the high single digits.

**Known limitations, in order of how much they distort the answer:**

1. **One-stage terminal value.** 70–78% of enterprise value sits in a perpetuity that starts after year five.
   The fix is a two-stage fade (10–15 years of fading growth, then perpetuity), which would raise both fair
   values materially.
2. **Terminal growth applied to a 2.5% assumption for businesses that are not 2.5% businesses.** The reverse
   DCF is the honest way to present this, which is why it is in the script.
3. **Balance-sheet debts are under-tagged.** KO shows zero long-term debt because the us-gaap concept it uses
   differs from Apple's — the same inconsistency that produced the `NULL` leverage in the first ratio table.
   Use `Liabilities` as a crude proxy, or add the missing concepts per company.
4. **Working capital is modelled as a percentage of the revenue change**, not built from receivables,
   inventory and payables. Acceptable for a demo, not for a published note.
5. **KO's beta is not usable** (R² 0.06: the market explains 6% of Coca-Cola's daily movement). Either use a
   longer window, a sector beta, or a beta built from a consumer-staples index — and say which.

## What this proves for the portfolio

The same repository now values a bank on residual income and a non-financial on discounted cash flow, from the
same data layer, with every assumption printed and every number replayable by one command. That is the
difference between "I know how to do a DCF" and "here is a DCF, here is what it assumes, and here is exactly
where it breaks."
