-- bank_queries.sql — bank analysis (Arab Bank: FY2024, FY2025, H1 2026)
-- Needs the manual figures loaded first:
--   python3 scripts/load_manual.py --csv data/manual/arabbank_figures.csv
-- Run with:  python3 scripts/run_queries.py --sql sql/bank_queries.sql

.headers on
.mode column

-- Q1. Sanity check: what have you entered, by period?
SELECT period, COUNT(*) AS items_entered, GROUP_CONCAT(item, ', ') AS items
FROM manual_figures
GROUP BY period, year, is_interim
ORDER BY year, is_interim;

-- Q2. The bank ratio panel — the table that goes into the note.
--     ROE is annualised for interim periods, so H1 is comparable with a full year.
SELECT period, roe_pct, income_to_cost_x, nim_on_assets_pct,
       loans_to_deposits_pct, npl_ratio_pct, npl_coverage_pct, car_pct
FROM bank_ratios
ORDER BY year, is_interim;

-- Q3. Movement in the two ratios that matter most.
SELECT period, roe_pct,
       LAG(roe_pct) OVER (ORDER BY year, is_interim) AS roe_prev,
       ROUND(roe_pct - LAG(roe_pct) OVER (ORDER BY year, is_interim), 1)  AS roe_change_pp,
       income_to_cost_x,
       ROUND(income_to_cost_x - LAG(income_to_cost_x) OVER (ORDER BY year, is_interim), 2) AS efficiency_change
FROM bank_ratios
ORDER BY year, is_interim;

-- Q4. Valuation versus performance: P/B and P/E, where price and share count were entered.
SELECT period, price, shares_m, market_cap_m, pb_x, pe_x
FROM bank_multiples
ORDER BY year, is_interim;

-- Q5. The question that makes a bank note worth reading: what ROE does the market's P/B imply?
--     Sustainable growth: P/B = (ROE - g) / (COE - g)  ->  implied ROE = P/B * (COE - g) + g
--     Change the two assumptions below and defend them in the note.
WITH assumptions AS (SELECT 0.16 AS coe, 0.04 AS g)
SELECT m.period, m.pb_x,
       ROUND(m.pb_x * (a.coe - a.g) + a.g, 3) AS implied_roe
FROM bank_multiples m CROSS JOIN assumptions a
ORDER BY m.year, m.is_interim;

-- Q6. Why a DCF on a bank misleads, demonstrated rather than asserted.
--     A bank's interest expense is an operating cost, not financing, so FCFF has no meaning here.
--     The asset-to-equity gearing is the thing that would have to be modelled — and it is regulated.
SELECT period,
       ROUND(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) AS total_assets_m,
       ROUND(MAX(CASE WHEN item = 'total_equity' THEN value END), 0) AS equity_m,
       ROUND(MAX(CASE WHEN item = 'total_assets' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_equity' THEN value END), 0), 1) AS assets_to_equity_x
FROM manual_figures
GROUP BY period, year, is_interim
ORDER BY year, is_interim;
