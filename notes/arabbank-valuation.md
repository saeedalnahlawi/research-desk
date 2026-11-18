# Arab Bank (ASE: ARBK) — valuation note

_Analysis prepared 18 November 2026. Data: Arab Bank Group consolidated financial statements FY2025
(audited) and condensed interim financial information for the six months to 30 June 2026; market data as at
18 November 2026. Sources and page references: `SOURCES.md`._

_Personal research, for educational purposes, not investment advice._

## 1. Method — and why not a DCF

A DCF is the wrong instrument for a bank. Discounting free cash flow to the firm requires separating operating
from financing cash flows, but for a bank **interest expense is an operating cost** and debt is its raw
material; FCFF has no economic meaning. What a bank valuation actually asks is:

> What return on equity does this bank earn, and what is that return worth relative to its book value?

So the model is an **excess-return (residual income) valuation**:

```
Value = Book equity today
      + Σ  (ROE_t − COE) × Book equity_{t-1}  / (1 + COE)^t
      + terminal value of the excess return, grown at g
```

Each year a bank earns ROE on its equity. If ROE exceeds the cost of equity, that surplus belongs to
shareholders and adds to the value of book; if ROE is below COE, retained earnings destroy value and the bank
should trade *below* book. This is why P/B is the multiple that matters and why "cheap on P/E" is not an
argument.

## 2. Starting point (all from the filings)

| Item | FY2024 | FY2025 | H1 2026 |
|---|---|---|---|
| Total income (USD m) | 3,395.0 | 3,586.0 | 1,844.3 |
| Net interest income | 2,145.3 | 2,135.3 | 1,041.2 |
| Net commission income | 453.1 | 527.0 | 275.7 |
| Operating expenses (ex-ECL) | 1,414.9 | 1,573.9 | 805.9 |
| Efficiency ratio | 41.7% | 43.9% | 43.7% |
| Impairment (ECL) | 490.7 | 423.2 | 221.0 |
| Profit for the year | 1,007.1 | 1,130.4 | 570.9 |
| Total equity | 12,134.9 | 13,233.0 | 13,531.8 |
| NPL ratio | 7.30% | 6.04% | 6.19% |
| Capital adequacy | 17.16% | 17.04% | 17.34% |

Derived: FY2025 implied tax rate **27.3%**; ROE on opening equity **8.5%**; book value per share
**JOD 14.95**; share price **JOD 7.47** → **P/B 0.50×**; implied ROE at that multiple (COE 11%, g 4%)
≈ **8.5%**.

## 3. What the trends say before any model

- **Asset quality improved sharply:** NPLs 7.30% → 6.04% → 6.19%. Credit costs fell from 490.7 to 423.2.
- **The earning engine is drifting the other way:** NIM on assets 3.0% → 2.7% → 2.6%, and the efficiency
  ratio worsened 41.7% → 43.9%. H1 2026 net interest income is *down* 1.5% year on year while total income grew
  3.2% — commission income (+16.3% in FY2025) is carrying the top line.
- **Profit growth came from lower provisions, not from the core.** Strip the ECL improvement and FY2025 pre-tax
  profit is roughly flat year on year.
- **Associates are 628.6m of 1,130.4m profit** — more than half of reported earnings comes from holdings rather
  than lending. This is a held company with a bank attached, not a plain retail bank, and it is why the
  exchange's quoted P/E (8.29, which appears to exclude the associates' share) differs from a P/E on total
  profit.

That sets the central question: **can a bank with a shrinking margin and a rising cost ratio convert its cleaner
loan book into a higher ROE?** The forecast below says: only partially.

## 4. Forecast

Drivers, each tied to a number observed above:

| Driver | 2026E–2030E | Reasoning |
|---|---|---|
| Total income growth | +4.0%, +3.8%, +3.6%, +3.5%, +3.5% | Slightly above FY2025's +5.6% initially, decaying; commission growth offsets NIM pressure |
| Excellence ratio (opex ex-ECL / income) | 43.7% rising to 44.5% | Continuing the observed 41.7% → 43.9% trend; no cost programme assumed |
| ECL / total income | 12.0% | FY2025 11.8%, H1 2026 12.0%; assumes no further normalisation |
| Tax rate | 27.3% | Implied FY2025 |
| Dividend payout | 40% | Assumption — dividend history not yet entered in the repo; 60% retained |

Base-case output (USD m):

| Year | Income | Profit | ROE |
|---|---|---|---|
| 2026E | 3,729 | 1,201 | 8.9% |
| 2027E | 3,871 | 1,238 | 8.7% |
| 2028E | 4,011 | 1,277 | 8.5% |
| 2029E | 4,151 | 1,315 | 8.4% |
| 2030E | 4,296 | 1,358 | 8.2% |

ROE **falls** even as profit rises, because equity compounds at ~5% a year while profit grows at ~3%. That is
the arithmetic of a bank retaining earnings at a return below its cost of capital.

## 5. Cost of equity — the assumption the whole valuation hangs on

CAPM, `COE = risk-free + beta × equity risk premium`:

| Risk-free | Beta | ERP | COE |
|---|---|---|---|
| 4.5% | 0.8 | 5.0% | 8.5% |
| 5.0% | 1.0 | 5.0% | 10.0% |
| 5.0% | 1.0 | 5.5% | 10.5% |
| 5.0% | 1.2 | 5.5% | 11.6% |

**Chosen: 11.0%**, at the conservative end of that band: Jordanian dinar risk-free rate around 5% (the CBJ's
policy stance and dinar deposit rates), a market risk premium of 5–5.5% for a small, concentrated exchange, and
a beta near 1.1 for a large bank. **Beta is assumed, not estimated** — no price history for the index has been
loaded into the repo yet. That is the model's weakest input and the first thing to fix.

An earlier version of this note used **16%**, which the CAPM build above does not support for a dinar-denominated
Jordanian bank; at 16% almost any bank looks overvalued. The correction matters: fair value roughly doubles
between a 16% and an 11% cost of equity, so the discount rate is doing more work than any forecast assumption.

## 6. Valuation

Fair value per share (JOD), market price 7.47:

| COE | g | Bear | Base | Bull |
|---|---|---|---|---|
| 10% | 4% | 8.05 | 10.48 | 14.20 |
| **11%** | **4%** | **6.89** | **8.92** | **12.05** |
| 12% | 4% | 6.02 | 7.75 | 10.45 |
| 14% | 4% | 4.81 | 6.12 | 8.21 |
| 16% | 4% | 4.00 | 5.04 | 6.73 |

Cross-check by the justified multiple: `justified P/B = (ROE − g)/(COE − g)` at ROE 8.5%, COE 11%, g 4% gives
**0.64×** book = JOD 9.57; at COE 12% it gives **0.56×** = JOD 8.37. The two methods agree within a few percent,
which is the test that the model is internally coherent.

## 7. Decision

**Fair value: JOD 8.00–9.00 per share in the base case** (central estimate **JOD 8.90**), against a market price
of 7.47 — roughly **7% to 20% above market**, i.e. **fairly valued to modestly undervalued at 0.50× book**.

Probability-weighted across the three scenarios (20% bear, 60% base, 20% bull at COE 11%): **~8.9 JOD**.

**Why this is not a strong buy**, even with upside:

1. **ROE (8.2–8.9%) is below the cost of equity (11%)** for the whole forecast. A bank earning less than its
   cost of capital should trade *below* book, and it does. The upside comes from book compounding at a discount,
   not from value creation.
2. **The margin and cost trends are negative.** NIM 3.0% → 2.6%; efficiency 41.7% → 43.9%. If both continue,
   the bear case (6.89) is the relevant one and the shares are expensive.
3. **More than half of profit is associates.** That value depends on holdings whose own performance is outside
   this model. A sum-of-parts analysis is the honest next step, not a refinement of the DCF.

**What would change the view — and the number to watch:**

- **NIM stabilising above 2.8%** with the efficiency ratio back below 42% → base case moves toward 10.5 JOD.
- **NPLs re-accelerating above 7%** or ECL above 13% of income → bear case, 6.9 JOD or lower.
- **ROE reaching 10%+** on a smaller equity base (higher payout) → the justified P/B moves to 0.86×, i.e. 12.9 JOD.
- **Beta actually estimated** from ASE index data: if it comes out below 1.0, COE falls toward 10% and the base
  case rises to ~10.5 JOD. This single input moves the answer more than the forecast does.

## 8. Known weaknesses of this note

1. Beta is assumed, not measured. Without it, COE — and therefore the entire valuation — is an opinion.
2. Dividend payout (40%) is an assumption; the dividend history is not yet in the repo.
3. ECL normalisation is held flat at 12% of income; a genuine credit cycle is not modelled.
4. Associates (628.6m of profit) are valued only through the ROE they contribute, not separately.
5. Quarterly seasonality is ignored; the model runs on full-year and interim-annualised figures.

Fixing (1) and (2) is a few hours of data work and would make this a defendable piece of research rather than a
structured estimate.
