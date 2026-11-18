# Telecom valuation engine

`scripts/value_telecom.py` values telecom operators: DCF on FCFF plus two multiple cross-checks, reconciled
rather than averaged. Built because a generic DCF hides the two things that decide a telecom's value — capex
intensity and the terminal assumption — and because blending three methods without checking they agree is how
a 17× P/E gets published as "fair value" for a 12× sector.

## How to run it

```bash
python3 scripts/value_telecom.py --profile profiles/jtel.json
python3 scripts/value_telecom.py --profile profiles/jtel.json --beta 1.0 --discount 0.30
```

Overrides available: `--beta`, `--rf`, `--erp`, `--g`, `--discount` (peer size/liquidity discount), `--margin`,
`--capex`.

## Profiles

A profile is a JSON file holding the base year, the forecast assumptions, the WACC inputs and the peer
multiples — everything a valuation needs, in one readable file. `profiles/jtel.json` is Orange Jordan.

For a US-listed operator, generate a starting profile:

```bash
python3 scripts/fetch_sec.py --tickers T
python3 scripts/load_sqlite.py
python3 scripts/fetch_prices.py --tickers T --years 5
python3 scripts/profile_from_edgar.py --ticker T --price-file data/prices/T.csv --beta 0.70 --capex-pct 0.13
```

**The generated profile is a draft, not an answer.** EDGAR tagging differs by filer: AT&T, for example, does
not tag `PaymentsToAcquirePropertyPlantAndEquipment` (capex had to be supplied as a percentage) or
`StockholdersEquity` (fell back to the NCI-inclusive concept). Verify net debt, capex and share count against
the filing before quoting a number.

## What the output contains

1. Base-year summary with market multiples at the current price.
2. **WACC with market weights** — the correction that matters most: book weights overstate the debt share and
   understate the discount rate.
3. Eight-year FCFF forecast, mid-year discounting by default.
4. DCF with the terminal share of EV stated (a telecom above ~70% is normal and must be disclosed).
5. Peer multiples with an explicit **size/liquidity discount**, applied to LTM EBITDA and net income.
6. **Reconciliation**: what P/E implies for EV/EBITDA and vice versa, plus the D&A intensity that causes the gap.
7. **Plausibility gate**: flags a DCF more than 2× the market price, an implied EV/EBITDA outside 2–15×, or
   capex below 8% of revenue. A telecom that fails these is usually a data problem, not an insight.
8. **Reverse DCF**: the WACC and the terminal growth the market price implies.
9. Sensitivity grids: WACC × g, and EBITDA margin × capex intensity.

## Orange Jordan (JTEL) — result

Base year FY2023: revenue 360.7m, EBITDA 146.5m (40.6%), D&A 83.0m, capex 72.1m, net debt 6.3m,
price 2.90 (12 Dec 2024), 187.5m shares.

| Method | Per share | vs market | Implied P/E |
|---|---|---|---|
| DCF (WACC 10.48%, g 2%, mid-year) | **4.01** | +38% | 16.4× |
| EV/EBITDA (peers 6.51× → 5.21× after 20% discount) | **4.04** | +39% | — |
| P/E (peers 12.5× → 10.0× after discount) | 2.44 | −16% | 10.0× |
| Market | 2.90 | — | 11.9× |

**Why the P/E leg disagrees (and it is not noise):** D&A is 23% of revenue. With that much depreciation, a
P/E multiple and an EBITDA multiple describe different companies. The P/E leg implies EV/EBITDA of only
**3.17×** while the peer median is 6.51×; the EV/EBITDA leg implies a P/E of 16.7× against a peer median of
12.5×. For a capital-intensive operator, **EV/EBITDA is the primary method and P/E is a sanity check** — the
divergence gets explained in the note, not averaged away.

**What the market is saying** (reverse DCF at the 2.90 price): either a **13.79% cost of capital** (model:
10.48%), or **terminal growth of −5.5%** (model: +2%). The market is pricing decline or a much higher risk
premium, not the model's flat-to-modest growth.

**Conclusion for the note:** fair value **3.60–4.05 JOD** (DCF and EV/EBITDA agree within 1%), against 2.90 —
roughly **20–40% upside**, but the argument rests on the forecast and the terminal assumption, not on the
multiples. State the market's implied decline explicitly; that is the strongest paragraph available.

## Known limitations

1. **Revenue growth is a percentage path, not a subscriber/ARPU build.** A proper telecom model forecasts
   subscribers × ARPU × churn and lets revenue fall out. The engine takes revenue growth as an input.
2. **Capex is a flat percentage of revenue.** Real telecoms alternate between investment cycles (5G, spectrum)
   and harvest years; a flat percentage smooths the thing that matters.
3. **D&A is a flat percentage**, so NOPAT and FCFF inherit a simplified tax shield.
4. **Working capital is 2% of the revenue change**, not built from receivables and payables.
5. **Peer multiples are static**, entered by hand. They drift; a quarterly refresh is needed before any
   published note.
6. **No licence/regulatory modelling** — for JTEL the telecom licence payable is inside net debt, but a renewal
   or spectrum payment would need its own line.
