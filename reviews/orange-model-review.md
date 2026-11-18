# Review — Orange Jordan (JTEL) forecasting model ("draft-final with graphs")

_Reviewed 19 Nov 2026. Eight sheets: Financials, Assumptions, ratios, WACC, DCF Valuation, Multiples,
ASE—JTEL, Graphs._

## What is genuinely strong

This is not a student spreadsheet with a DCF bolted on. The detail is real work:

- **Revenue built from drivers**, segment by segment — fixed voice, mobile, data services, payment services —
  each with its own growth path and inter-segment lines, not one top-line growth number.
- **Subscriber build** with y-o-y growth feeding the segments, and market-share context.
- **Working capital on days** (receivables 110, inventory 30, payables 350), so the balance sheet rolls off
  revenue rather than being pasted in.
- **IFRS 16 handled**: right-of-use assets and lease liabilities both modelled, with their own amortisation.
- **Capex split into four lines**, tax at 26%, dividends, and a full balance sheet that balances.
- Eight-year explicit forecast (2024F–2031F), perpetual growth at 2%, a sensitivity grid, and a three-method
  blend (60% DCF / 25% EV/EBITDA / 15% P/E).

For a graduate portfolio that is well above the usual standard. The problems below are fixable; the skeleton is
worth keeping.

## Defects, ranked by how much they change the answer

### 1. The DCF contradicts the multiples in the same model — and the blend hides it

| Basis | Per share | Implied P/E | Implied P/B |
|---|---|---|---|
| DCF | 4.139 JOD | **17.0×** | **2.55×** |
| EV/EBITDA | 4.981 | 20.4× | — |
| P/E | 3.106 | 12.7× | — |
| **Blend (60/25/15)** | **4.196** | **17.2×** | **2.58×** |
| Market (2.90) | 2.90 | 11.9× | 1.78× |
| Peer average | — | 12.73× | — |

The DCF concludes the shares are worth **17× earnings and 2.6× book** — for a single-country operator whose
revenue is growing about 4% — while the same workbook prices eight comparable telecoms at **12.7×**. And the
P/E leg, at 3.106, is the one method that agrees with the peer set, so it receives the smallest weight (15%).

That is the first thing a reviewer (or a CFA judge) will notice: **the three methods are not triangulating, they
are being averaged away from each other.** A blend is legitimate only when the methods disagree for explainable
reasons, and the reasons have to be written down.

### 2. WACC weights are book-based, not market-based

The WACC sheet weights debt and equity using **book** debt (73.1m) and **book** equity (304.8m): 19.3% / 80.7%.
Weighted average cost of capital must use **market** values, because that is the mix the company actually
operates with.

| | Debt weight | Equity weight | WACC | Fair value/share |
|---|---|---|---|---|
| Book weights (as modelled) | 19.3% | 80.7% | 11.60% | 4.139 |
| **Market weights** | **11.9%** | **88.1%** | **12.23%** | **3.703** |

Market weights raise WACC by 63bp and cut fair value by **11%**. This one correction does more than any
forecast assumption in the model.

### 3. Beta of 1.08 rests on 13 monthly observations

The `ASE—JTEL` sheet contains **13 monthly price points** (2.54 → 2.90) against the JOSMGNFF index. If that is
where 1.08 came from, it is not a beta — it is noise with a decimal point. Standard practice is 60 monthly or
250+ daily returns; with 13 points the standard error swamps the estimate.

Either extend the price history, or state that beta is an assumption and justify it (a large, low-volatility
telecom would ordinarily sit at 0.6–0.9, not 1.08).

### 4. The peer set is not comparable to Orange Jordan

Emirates Integrated, Vodafone Qatar, Zain (Kuwait), e&, Omantel, Ooredoo, Mobily, STC: every one is larger,
multi-country, and several are state-linked. Orange Jordan is a **single-country, sub-US$1bn, low-growth**
operator. Averaging those multiples straight gives 6.42× EV/EBITDA, and applying it without adjustment assumes
a size and liquidity premium of zero — which does not exist in practice. A 20–30% discount to the peer average,
with the reason stated, would be defensible; a straight average is not.

### 5. Multiples are applied to the wrong year

`Multiples!A20` applies the 6.42× average to **FY2023 EBITDA** (146.47m), while the peer multiples are current
(LTM/forward). Freeze a 2023 EBITDA against a 2026 multiple and you understate EV by 9.4m for no reason. Use
2024E or LTM on both sides of the comparison.

### 6. The workbook is not portable

The `ratios` sheet formulas reference an **external workbook** (`[2]Financials!B17` etc.), not the internal
sheet. Open the file on another machine — which is exactly what an interviewer, a judge or a recruiter will do —
and those rows can show stale values or `#REF`. Every reference should be internal (`Financials!B17`).

## Smaller items worth fixing before this is published

- **Discounting convention**: 2024F is discounted at t=0, i.e. treated as already received. Defensible if the
  valuation date is 31 Dec 2024 and FY2024 is effectively actual, but the note must say so, and the date used
  for "last closing price" (2.90, 12 Dec 2024) should match the valuation date.
- **Payment services growth of +100%, then +70%, then +55%** is a large assumption with no citation. Either
  source it (management guidance, market data) or fade it faster.
- **Terminal value is 46% of EV** — normal for telecoms, and worth stating explicitly in the note as a
  sensitivity, not leaving it implicit.
- **The 60/25/15 blend has no stated rationale.** Write one sentence per weight, or drop the blend and publish
  the football field with a chosen point.
- **Cross-check the DCF against the multiples *before* blending.** If the DCF implies 17× P/E and peers trade at
  12.7×, the honest move is to ask why — higher margins? lower capex? — not to average the two away.

## The number that matters

At the market price of 2.90 the shares trade on **11.9× earnings and 1.78× book**. The model's blend says
**4.196 — a 45% upside**. Even after correcting only the WACC weights (the one unambiguous error), the answer
falls to ~3.70, still 28% above market. So the conclusion survives the correction — but it survives *because of
the forecast*, not because of the multiples, and the note has to defend the forecast explicitly: flat-to-modest
revenue growth, capex discipline, and a 2% perpetuity.

## What to do with this file

1. **Do not publish it as-is** on LinkedIn. The book-weight WACC, the 13-point beta and the external links are
   the three things that turn a good model into a careless one when someone else opens it.
2. **Keep it** as the interview artifact, and prepare the "what I would change" answer — a candidate who can
   say *"my CFA model used book weights for WACC and a 13-month beta; here is the corrected version"* is far
   more credible than one presenting a flawless model.
3. **Rewrite it in `research-desk`** with the corrections above: market weights, a beta from 60+ monthly
   returns, an internal-reference clean workbook, and a note that states the discounting convention. That
   version can be published, because every number can be replayed.

## Compliance check before publishing

CFA Institute Research Challenge rules restrict what teams may publish about their submission. Confirm the
current rules before posting the report, the model or its conclusions publicly — the safe route is to publish a
**rewritten** analysis with your own updated assumptions and public data, not the submitted deliverable.
