# Which valuation method — and why the model changes with the sector

The *discipline* is identical for every company: drivers from the filings → forecast → discount → cross-check
against multiples → publish assumptions and limits. The *model* is not. Applying a DCF to a bank is the classic
error; applying a residual-income model to a manufacturer is the same error in reverse.

| Sector | Primary method | Cross-check | Never do this |
|---|---|---|---|
| Banks | Excess return / residual income; P/B against ROE | Justified P/B = (ROE−g)/(COE−g) | FCFF/DCF, EV/EBITDA — debt is raw material |
| Insurers | P/B vs ROE, dividend discount | Combined ratio trend, embedded value | EV/EBITDA |
| Industrials, consumer, telecom | DCF on FCFF; EV/EBITDA with a justified peer set | Comps + sum-of-parts if multi-division | Ignoring working-capital swings |
| Tech / SaaS | EV/revenue or EV/ARR when unprofitable; DCF with defensible churn | Rule of 40, net revenue retention, CAC payback | Treating implementation revenue as recurring |
| Real estate / REITs | NAV at market cap rates; FFO multiples | P/NAV, cap rates, LTV | Book value as a proxy for market value |
| Energy, utilities, mining | NAV of reserves or regulated asset base | EV/EBITDA per unit, reserve life | Valuing on spot prices without a stated long-run assumption |

## What changes when the company is US-listed (NYSE / NASDAQ)

1. **Data stops being manual.** EDGAR serves full XBRL for every filer — the same `scripts/fetch_sec.py`
   pipeline already pulls Apple and Coca-Cola. No hand entry, no page references; the accession number is the
   provenance instead.
2. **The cost of equity gets measured, not assumed.** Risk-free from the US Treasury curve at the forecast
   horizon, equity risk premium ~4.5–5.5%, and **beta estimated by regression** against the S&P 500 rather than
   picked. This removes the weakest input in the Arab Bank note.
3. **No FX layer.** For a USD filer, market cap and book are already in one currency; the JOD/USD trap that
   nearly broke P/B disappears. It returns the moment you value an ADR or a foreign private issuer.
4. **Richer disclosure, more assumptions to get wrong.** Segment reporting, stock-based compensation, lease
   accounting (ASC 842 vs IFRS 16), pension obligations, and — for tech — capitalised development costs. A DCF on
   a US name usually has 60–80% of its value in the terminal period, so the terminal assumptions *are* the
   valuation and must be shown in sensitivity form.
5. **Peer sets are easy to find and easy to get wrong.** Sector classification (GICS) is available, but size,
   geography and business mix still have to be justified by hand.

## What stays exactly the same

- Drivers from the statement, not from a growth rate someone liked.
- A forecast that shows ROE/ROIC against the cost of capital, so the value creation (or destruction) is visible.
- Two methods that must agree within a reasonable band, or the difference gets explained.
- A sensitivity grid, because a single fair-value number is a claim about precision that does not exist.
- A "what would change my view" section, and a list of the model's own weaknesses.

That last item is what separates research from opinion, and it is sector-independent.
