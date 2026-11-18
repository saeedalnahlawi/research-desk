# JTEL verification — every input traced to the audited statements

_19 Nov 2026. Purpose: before any of this goes on GitHub or LinkedIn, check the numbers against the primary
source rather than against the workbook they came from._

Source: **Jordan Telecommunications Company (Orange Jordan), Consolidated Financial Statements, year ended
31 December 2023**, in the FY2023 Annual Report (`data/source/orange-ar-2023.pdf`, 55 pages).
Page numbers below are PDF pages.

## Verified — exact match

| Item | Workbook / profile | Audited FS | Page | Result |
|---|---|---|---|---|
| Net revenue | 360,715,627 | 360,715,627 | p28 | ✅ exact |
| Direct operating cost | (132,187,360) | (132,187,360) | p28 | ✅ |
| Gross margin | 228,528,267 | 228,528,267 | p28 | ✅ |
| Administrative expenses | (23,187,104) | (23,187,104) | p28 | ✅ |
| Selling & distribution | (43,457,203) | (43,457,203) | p28 | ✅ |
| Government revenue share | (6,371,613) | (6,371,613) | p28 | ✅ |
| Support & brand fees | (8,441,945) | (8,441,945) | p28 | ✅ |
| Expected credit losses | (600,000) | (600,000) | p28 | ✅ |
| Depreciation — PPE | (60,326,946) | (60,326,946) | p28 | ✅ |
| Amortisation — intangibles | (13,559,979) | (13,559,979) | p28 | ✅ |
| Depreciation — right-of-use | (7,005,658) | (7,005,658) | p28 | ✅ |
| Depreciation — renewable energy | (2,112,343) | (2,112,343) | p28 | ✅ |
| **D&A total** | 83,004,926 | 60,326,946 + 13,559,979 + 7,005,658 + 2,112,343 | p28 | ✅ |
| **EBITDA (derived)** | 146,470,402 | revenue − five cash cost lines − ECL = 146,470,402 | p28 | ✅ |
| Profit for the year | 45,748,255 | 45,748,255 | p28 | ✅ |
| Earnings per share | 0.2440 | 45,748,255 ÷ 187,500,000 | p28 | ✅ |
| Paid-in capital / shares | 187,500,000 | 187,500,000 | p28 | ✅ |
| Total equity | 304,762,352 | 187,500,000 + 62,500,000 + 54,762,352 | p28 | ✅ |
| Total assets | 786,957,704 | 786,957,704 | p28 | ✅ |
| Total liabilities | 482,195,352 | 482,195,352 | p28 | ✅ |
| Cash & short-term deposits | 66,787,549 | 66,787,549 | p28 | ✅ |
| Interest-bearing loans | — | 634,696 | p28 | ✅ |
| Lease liabilities | — | 35,035,663 | p28 | ✅ |
| Operating cash flow | — | 124,213,666 | p29 | ✅ |

The income statement, balance sheet and EBITDA are **internally consistent to the dinar**. That part of the
workbook is sound.

## Corrected — two inputs were wrong

### 1. Capex: the profile used a *forecast*, not the actual

| | Value | % of revenue | Source |
|---|---|---|---|
| Used in the first run | 72,112,343 | 19.5% | DCF sheet, **2024F** — a forecast line |
| **FY2023 actual** | **84,671,439** | **23.5%** | p29: PPE purchases 78,327,614 + intangibles 6,343,825 |

This is the error that mattered. A base year must use reported capex; taking a forecast line as the base
smuggles a 12.6m assumption into every forecast year.

**Effect on the valuation — and it is not small:**

| Capex assumption | DCF fair value | vs market |
|---|---|---|
| 19.5% (forecast line, wrong) | 4.01 JOD | +38% |
| **23.5% (FY2023 actual)** | **2.94 JOD** | **+2%** |

Each percentage point of capex intensity is worth about **0.27 JOD per share**. For a telecom, capex is not a
detail — it is the valuation. Note also that FY2023 was an investment-heavy year (PPE purchases 78.3m against
53.1m in FY2022), so a normalised assumption would sit below 23.5% — that is a scenario to argue in the note,
not a reason to use the wrong base year.

### 2. Share price on the valuation date

| | Value | Source |
|---|---|---|
| Used in the workbook | 2.90 | "Last closing price in 12/12/2024" |
| **Actual close, 12 Dec 2024** | **2.88** | WSJ historical prices, JTEL (JO/XAMM); range 12.88–2.91 that week |

Immaterial to the answer (0.7%), but a published note must quote the actual close.

### 3. Flagged, not corrected — the telecom licence payable

The workbook's debt is 73,098,436 (loans + leases + one further component) and ignores the
**telecommunications licence payable of 59,689,361** (p28). Treating a regulatory licence obligation as
operating rather than financing is defensible — many analysts do — but it must be stated, because including it
takes net debt from 6.3m to ~65.9m and cuts fair value by roughly 0.32 JOD per share.

## The result after verification

| Method | Per share | vs 2.88 | Note |
|---|---|---|---|
| **DCF** (WACC 10.47%, g 2%, mid-year, actual capex) | **2.94** | **+2%** | the primary method for a telco |
| EV/EBITDA (peer 6.51× → 5.21×) | 4.04 | +40% | ignores capex intensity — the whole story |
| P/E (peer 12.5× → 10.0×) | 2.44 | −15% | distorts under 23% D&A/revenue |
| Market | 2.88 | — | 11.8× earnings, 1.77× book |

**Conclusion: Orange Jordan is fairly valued at 2.88.** The DCF, built from audited inputs, lands within 2% of
the market price — and the reverse DCF confirms it: the market is pricing a **10.65% cost of capital** and
**1.70% terminal growth**, against the model's 10.47% and 2.0%. There is no mispricing to exploit.

**The 43–45% "upside" in the original model was a capex artefact.** That is the sentence that belongs in the
note, and the sentence that belongs in any interview: *"My first version said 4.19 because I used a forecast
capex line as the base year. Against the audited 23.5%, it's 2.94 — the stock was priced correctly."*

## Sensitivity worth publishing

| EBITDA margin | capex 20% | capex 24% | capex 26% |
|---|---|---|---|
| 36.5% | 3.16 | 2.35 | 1.54 |
| 39.5% | 3.74 | **2.94** | 2.13 |
| 42.5% | 4.33 | 3.53 | 2.72 |

The honest statement is a range of **2.4–3.7 JOD** depending on margin and capex, with 2.94 at the base case —
not a single number pretending to precision.

## Peer multiples — refreshed 18 Nov 2026

Re-pulled from stockanalysis.com statistics pages (TTM EV/EBITDA and P/E), replacing the workbook's undated
figures:

| Peer | Exchange | EV/EBITDA | P/E |
|---|---|---|---|
| Emirates Integrated (du) | DFM | 9.03 | 14.53 |
| e& (Etisalat Group) | ADX | 9.74 | 16.50 |
| Saudi Telecom | Tadawul 7010 | 6.81 | 15.83 |
| Vodafone Qatar | QSE | 7.80 | 13.50 |
| Etihad Etisalat (Mobily) | Tadawul 7020 | 6.37 | 12.46 |
| Omantel | MSM | 5.12 | 8.62 |
| Zain Saudi | Tadawul 7030 | 5.12 | 10.28 |
| Ooredoo | QSE | 4.73 | 11.06 |
| **Median** | | **6.59×** | **13.0×** |

**Disclosure:** Zain Kuwait (KSE) has no TTM figures on the source used, so Zain Saudi is included in its place.
The set is eight GCC operators, all larger and more diversified than Orange Jordan — which is why the 20%
size/liquidity discount is applied.

The refreshed medians (6.59× / 13.0×) are close to the workbook's (6.42× / 12.5×): **the original peer numbers
were broadly right**, unlike the capex line. The multiples leg moves from 4.04 to 4.08 — the conclusion is
unchanged.

## Why the multiples leg still disagrees with the DCF

EV/EBITDA at 5.27× (post-discount) on EBITDA of 146.5m gives 4.08 JOD, while the DCF gives 2.94. The multiple
ignores capex, and the peer set is materially less capex-intensive than Orange Jordan at 23.5% of revenue. A
capex-adjusted check makes the point: `EBITDA − capex = 61.8m`, and at the same 6.59× that is an EV of ~407m,
or **2.14 JOD per share** — below the market. So the range across three framings is 2.14 / 2.94 / 4.08, and the
DCF sits sensibly in the middle. **Lead with the DCF; use the multiples as a bounded sanity check.**

## Still unverified
- **Beta 0.75** is an assumption, not an estimate. JTEL monthly data exists in the workbook (13 points) — too
  few for a regression; either extend the history or state it as an assumption.
- **WACC inputs** (rf 6.75%, ERP 6%) should be sourced and dated (Jordanian T-bill / CBJ, and a stated ERP
  reference) before they appear in a published note.
