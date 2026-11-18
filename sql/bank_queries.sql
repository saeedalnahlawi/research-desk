-- bank_queries.sql — bank-specific analysis (Arab Bank)
-- Needs the manual figures loaded first:
--   python3 scripts/load_manual.py --csv data/manual/arabbank_figures.csv
-- Run with:  python3 scripts/run_queries.py --sql sql/bank_queries.sql
-- (rename the query labels B1..B5; run_queries.py matches any Qn/Bn label it finds as "Q\d+",
--  so to use this file pass --sql and edit the labels to Q1..Q5 or run the statements directly.)

.headers on
.mode column

-- Q1. Sanity check: what have you actually entered, by year and item?
SELECT year, COUNT(*) AS items_entered, GROUP_CONCAT(item, ', ') AS items
FROM manual_figures
GROUP BY year
ORDER BY year DESC;

-- Q2. The bank ratio panel — the table that goes into the note.
SELECT year, roe_pct, income_to_cost_x, nim_on_assets_pct, deposits_to_assets_pct,
       loans_to_deposits_pct, npl_ratio_pct, npl_coverage_pct, car_pct
FROM bank_ratios
ORDER BY year;

-- Q3. Year-over-year movement in the two ratios that matter most.
SELECT year, roe_pct,
       LAG(roe_pct) OVER (ORDER BY year) AS roe_prev,
       ROUND(roe_pct - LAG(roe_pct) OVER (ORDER BY year), 1) AS roe_change_pp,
       income_to_cost_x,
       ROUND(income_to_cost_x - LAG(income_to_cost_x) OVER (ORDER BY year), 2) AS efficiency_change
FROM bank_ratios
ORDER BY year;

-- Q4. Valuation versus performance: P/B and P/E from share price and share count.
--     Add rows for 'share_price' and 'shares_outstanding' to the CSV for the date you want.
WITH mkt AS (
    SELECT year,
           MAX(CASE WHEN item = 'share_price' THEN value END)       AS price,
           MAX(CASE WHEN item = 'shares_outstanding' THEN value END) AS shares_m
    FROM manual_figures GROUP BY year
),
eq AS (
    SELECT year,
           MAX(CASE WHEN item = 'total_equity' THEN value END) AS equity,
           MAX(CASE WHEN item = 'net_profit' THEN value END)   AS net_profit
    FROM manual_figures GROUP BY year
)
SELECT m.year,
       m.price, m.shares_m,
       ROUND(m.price * m.shares_m, 1)                AS market_cap_m,
       ROUND(m.price * m.shares_m / NULLIF(e.equity, 0), 2)     AS pb_x,
       ROUND(m.price * m.shares_m / NULLIF(e.net_profit, 0), 2) AS pe_x
FROM mkt m JOIN eq e ON e.year = m.year
WHERE m.price IS NOT NULL AND m.shares_m IS NOT NULL
ORDER BY m.year;

-- Q5. The question that makes a bank valuation: what ROE does the market's P/B imply?
--     Sustainable-growth identity: P/B = (ROE - g) / (COE - g).
--     Rearranged for ROE given an assumed cost of equity and growth:
--       implied_ROE = P/B * (COE - g) + g
--     Change the two numbers in the CTE to your own assumptions and defend them.
WITH assumptions AS (SELECT 0.16 AS coe, 0.04 AS g),
mkt AS (
    SELECT year,
           MAX(CASE WHEN item = 'share_price' THEN value END)       AS price,
           MAX(CASE WHEN item = 'shares_outstanding' THEN value END) AS shares_m,
           MAX(CASE WHEN item = 'total_equity' THEN value END)       AS equity
    FROM manual_figures GROUP BY year
)
SELECT m.year,
       ROUND(m.price * m.shares_m / NULLIF(m.equity, 0), 2) AS pb_x,
       ROUND((m.price * m.shares_m / NULLIF(m.equity, 0)) * (a.coe - a.g) + a.g, 3) AS implied_roe
FROM mkt m CROSS JOIN assumptions a
WHERE m.price IS NOT NULL
ORDER BY m.year;
