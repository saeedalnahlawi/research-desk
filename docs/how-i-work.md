# How I work

I value listed companies and publish the model, the data and the assumptions — including the ones I got wrong.
Every number in every note traces to a filing or a dated market source, and every note can be re-run from this
repository.

I learned the method in the CFA Institute Research Challenge and in my Financial Technology degree. The work
below is independent: my own assumptions, my own data pulls, and conclusions that sometimes contradict the
original academic exercise. Where a figure was corrected after checking the audited statements, the correction is
documented rather than quietly fixed.

## Standards I hold myself to

1. **Primary sources only.** Audited financial statements, exchange filings, central bank rates. Not aggregator
   data, not someone else's spreadsheet.
2. **Every input has a page reference or a date.** If I cannot cite it, it does not go in the model.
3. **Two methods that must agree within a stated band** — or the disagreement gets explained. Averaging two
   valuations that disagree is not analysis.
4. **Sensitivity, not precision.** A single fair-value number is a claim about accuracy that does not exist. I
   publish a range and the assumptions that move it.
5. **A "what would change my view" section** in every note, with the specific metric to watch.
6. **The limitations get published too.** Beta assumed rather than measured, capex smoothed, peers larger than
   the subject — all stated, not buried.
7. **Corrections are public.** If a later check changes a number, the note says so and says why.

## Method by sector

The valuation method follows the business, not the exchange:

- **Banks:** excess-return (residual income), P/B against ROE, justified P/B = (ROE − g)/(COE − g).
  Not DCF — interest expense is an operating cost and debt is the raw material.
- **Telecoms:** DCF on FCFF with capex modelled explicitly, cross-checked against EV/EBITDA (with a
  size/liquidity discount) and P/E. Capex intensity decides the answer, so it gets its own sensitivity.
- **Industrials and consumer:** DCF on FCFF, EV/EBITDA with a justified peer set, working capital modelled.

## What is in this repository

| Layer | Where |
|---|---|
| Data ingestion | `scripts/fetch_sec.py` (EDGAR), `scripts/fetch_prices.py`, manual entry for ASE filers |
| Analysis | `sql/*.sql`, `scripts/run_queries.py` |
| Valuation engines | `scripts/value_bank.py`, `scripts/value_dcf.py`, `scripts/value_telecom.py` |
| Inputs per company | `profiles/*.json` — every assumption visible in one file |
| Notes | `notes/` — the published analysis |
| Reviews and verification | `reviews/` — model critiques and source verification |

## Disclaimer

This is personal research, published for educational purposes. It is not investment advice, not a
recommendation to buy or sell any security, and not a solicitation. I hold no position in the companies analysed
unless stated. Any reader should do their own work.
