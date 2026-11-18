# Sources — Arab Bank figures

Every number in `data/manual/arabbank_figures.csv` traces to a page below. Page numbers are **PDF page
numbers** as counted by a PDF reader, not the printed page number in the document's footer.

## Documents

| Ref used in CSV | Document | URL |
|---|---|---|
| `FS-2025 p…` | Arab Bank Group — Consolidated Financial Statements, year ended 31 December 2025 (115 pages; carries 2025 and 2024 comparatives) | https://www.arabbank.jo/docs/default-source/annual-reports-sorted/arab-bank-group-financial-statements-2025.pdf |
| `Q2-2026 p…` | Arab Bank Group — Condensed Consolidated Interim Financial Information, six months ended 30 June 2026 (38 pages) | https://www.arabbank.jo/docs/default-source/quarterly-reports/arab-bank-group-financial-statements-q2-2026.pdf |
| `FS-2024 p…` | Consolidated Financial Statements, year ended 31 December 2024 (115 pages) — only needed if a 2024 line is missing from the 2025 file | https://www.arabbank.jo/docs/default-source/annual-reports-sorted/arab-bank-group-financial-statements-2024.pdf |

Reporting currency: **USD thousands**. The CSV stores USD millions, so each figure is the reported number
divided by 1,000.

## Page map

### FY 2025 (comparatives for FY 2024 on the same pages)

| Item | Page | Notes |
|---|---|---|
| Interest income | p10 | 4,005,207 (2025) / 4,013,607 (2024) |
| Interest expense | p10 | 1,869,926 / 1,868,321 |
| Net interest income | p10 | check: income − expense, both years |
| Net commission income | p10 | 527,036 / 453,068 |
| Total income | p10 | 3,586,023 / 3,395,007 |
| Employees' expenses | p10 | 861,424 / 786,204 |
| Other expenses | p10 | 567,389 / 511,212 |
| Depreciation and amortisation | p10 | 145,073 / 117,551 |
| Provision for impairment (ECL) | p10, note 6 | 423,153 / 490,730 |
| Total expenses | p10 | 2,030,774 / 1,949,497 — includes ECL and other provisions |
| Profit for the year | p11 | 1,130,356 / 1,007,090 (after tax) |
| Profit attributable to shareholders | p115 | 1,083,344 / 969,126 — use this for EPS-based ratios |
| Total assets | p9 | 78,187,703 / 71,230,521 |
| Direct credit facilities — net | p9 | 37,479,274 / 34,383,335 |
| Customers' deposits | p9 | 54,624,469 / 49,775,767 |
| Total shareholders' equity | p9 | 13,233,002 / 12,134,899 (includes perpetual tier 1) |
| Non-performing loans | p59 (2025), p60 (2024) | 2,488.9m / 2,787.3m, stated in the note text in USD millions |
| NPL ratio | p59 / p60 | 6.04% / 7.30% of total direct credit facilities (as stated) |
| Capital adequacy ratio | p113 | 17.04% / 17.16%; CET1 14.51% / 14.64%; tier 1 15.54% / 15.77% |
| Shares outstanding | p115 | average number of shares: 640,800 thousand |

### H1 2026

| Item | Page | Notes |
|---|---|---|
| Interest income | p5 | 1,898,430 (six months) |
| Interest expense | p5 | 857,268 |
| Net interest income | p5 | 1,041,162 |
| Net commission income | p5 | 275,735 |
| Total income | p5 | 1,844,335 |
| Employees' expenses | p5 | 450,685 |
| Other expenses | p5 | 283,886 |
| Depreciation and amortisation | p5 | 71,311 |
| Expected credit loss | p5 | 221,029 |
| Total expenses | p5 | 1,038,197 |
| Profit for the period | p6 | 570,855 (six months); attributable 546,990 on p35 |
| Total assets | p4 | 80,334,142 at 30 June 2026 |
| Direct credit facilities — net | p4 | 38,294,647 |
| Customers' deposits | p4 | 56,457,952 |
| Total equity | p4 | 13,531,795 |
| Non-performing loans | p17 | 2,606.3m |
| NPL ratio | p17 | 6.19% (as stated) |
| Capital adequacy ratio | p33 | 17.34%; CET1 14.71%; tier 1 15.87% |
| Shares outstanding | p35 | 640,800 thousand |

## Market data (price and FX) — the part that is not in the statements

Arab Bank (ARBK) trades on the Amman Stock Exchange in **JOD**; the statements are in **USD**. Both inputs
are therefore needed, and the currency conversion is where a P/B quietly goes wrong by ~40%.

| Period | Closing price (JOD) | Date used | Source |
|---|---|---|---|
| FY 2024 | 4.50 | 30 Dec 2024 (last trading day of 2024) | WSJ historical prices, ARBK (JO/XAMM) |
| FY 2025 | 6.85 | 31 Dec 2025 | WSJ historical prices, ARBK |
| H1 2026 | 7.23 | 30 Jun 2026 | WSJ historical prices, ARBK |

**FX rate: 0.708 JOD per USD**, from the Central Bank of Jordan's published rates (USD = 708 fils).
The dinar is pegged to the dollar, so the same rate is used for all three dates; state that rather than
implying a historical series was consulted.

Cross-check the current price against the exchange's own page (ase.com.jo/en/company_historical/ARBK) —
on 18 Nov 2026 it showed a closing price of 7.47 and a P/E of 8.29.

### Exchange-quoted P/E — adopted, dated, and disclosed

Decision (Saeed, 18 Nov 2026): **use the exchange's published P/E** rather than the model's own construction
where a P/E is quoted. It is stored in `data/manual/ase_quotes.csv` with its date and source, loaded into the
`ase_quotes` table, and reported by Q8 next to the model's figure:

| Quote date | ASE price (JOD) | P/E as published by ASE | Model P/E (latest period) | Gap |
|---|---|---|---|---|
| 2026-11-18 | 7.47 | **8.29** | 5.73 | +2.56 |

Reporting rule that comes with adopting it:

- Call it **"exchange-quoted P/E"**, never "computed" — the exchange does not document its basis, so the
  number is cited, not derived.
- State the quote date in any note that uses it. It is a market snapshot, not a fiscal-period figure.
- Disclose the gap (2.56x) in one line rather than hiding it. An unexplained difference between your number
  and the exchange's is fine to publish when labelled; silently substituting one for the other is not.
- **Prefer P/B for the valuation argument** (0.48x latest, computed from market cap ÷ book equity, replayable
  from the repo). P/E is supporting colour, not the spine of the note.

## Verified arithmetic

`bank_queries.sql` Q7 recomputes net interest income from interest income minus interest expense for all
three periods and compares it to the reported figure. Current result: **difference 0.000 in every period.**
If that column is ever non-zero, a figure was mistyped.
