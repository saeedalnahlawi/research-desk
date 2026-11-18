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

## Still missing — and why it matters

**Share price and the JOD/USD rate are not in the financial statements.** Arab Bank (ticker ARBK) trades on
the Amman Stock Exchange in **JOD**, while the statements are in **USD**. To compute P/B you need:

1. closing price in JOD on the balance-sheet date (31 Dec 2024, 31 Dec 2025, 30 Jun 2026) — ASE daily
   bulletin, or the exchange's historical price page;
2. the JOD/USD rate on the same date — Central Bank of Jordan published rate.

Enter both in the CSV (`Share price`, `FX rate (JOD per USD)`) and Q4/Q5 in `sql/bank_queries.sql` come
alive. Without the FX rate the view returns nothing, deliberately: a P/B mixing JOD market cap with USD book
value would be wrong by roughly 40%, and wrong by an amount a reader cannot see.

## Verified arithmetic

`bank_queries.sql` Q7 recomputes net interest income from interest income minus interest expense for all
three periods and compares it to the reported figure. Current result: **difference 0.000 in every period.**
If that column is ever non-zero, a figure was mistyped.
