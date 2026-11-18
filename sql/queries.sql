-- queries.sql — the Week 2 practice set, run against data/research.db
--   sqlite3 data/research.db < sql/queries.sql
-- Each block is a question you should be able to write from scratch by Week 4.

.headers on
.mode column

-- Q1. What does the raw data actually look like? (always start here)
SELECT ticker, concept, COUNT(*) AS rows, MIN(fy) AS first_fy, MAX(fy) AS last_fy
FROM facts
GROUP BY ticker, concept
ORDER BY ticker, rows DESC
LIMIT 20;

-- Q2. Revenue by year, per company. Note the NULL: some companies tag revenue
--     differently, which is the first real data-cleaning lesson.
SELECT ticker, end,
       MAX(CASE WHEN concept = 'Revenues' THEN value END)                             AS revenues,
       MAX(CASE WHEN concept = 'RevenueFromContractWithCustomerExcludingAssessedTax'
                THEN value END)                                                       AS revenue_contract
FROM annual
WHERE concept IN ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax')
GROUP BY ticker, end
ORDER BY ticker, end DESC;

-- Q3. Clean single revenue series using COALESCE — this is the line that should
--     end up in the repo, not two stacked columns.
SELECT ticker, end,
       COALESCE(MAX(CASE WHEN concept = 'Revenues' THEN value END),
                MAX(CASE WHEN concept = 'RevenueFromContractWithCustomerExcludingAssessedTax'
                         THEN value END)) AS revenue
FROM annual
WHERE concept IN ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax')
GROUP BY ticker, end
ORDER BY ticker, end DESC;

-- Q4. Three core ratios per company, latest fiscal year: net margin, ROE, leverage.
--     Note the joins are LEFT: a missing concept should show as NULL, not delete the row.
WITH latest_year AS (
    SELECT ticker, MAX(end) AS end FROM revenue_annual GROUP BY ticker
)
SELECT r.ticker,
       r.end                                     AS fiscal_year_end,
       ROUND(ni.value / NULLIF(r.revenue, 0) * 100, 1) AS net_margin_pct,
       ROUND(ni.value / NULLIF(eq.value, 0) * 100, 1)  AS roe_pct,
       ROUND(li.value / NULLIF(eq.value, 0), 2)        AS liabilities_to_equity
FROM revenue_annual r
JOIN latest_year ly ON ly.ticker = r.ticker AND ly.end = r.end
LEFT JOIN latest_annual ni ON ni.ticker = r.ticker AND ni.concept = 'NetIncomeLoss'
LEFT JOIN latest_annual eq ON eq.ticker = r.ticker AND eq.concept = 'StockholdersEquity'
LEFT JOIN latest_annual li ON li.ticker = r.ticker AND li.concept = 'Liabilities'
ORDER BY r.ticker;

-- Q5. Window function: year-over-year revenue growth. This is the Week 2 gate.
--     LAG() is why real analysts stopped doing this in Excel.
WITH rev AS (SELECT ticker, end, revenue FROM revenue_annual)
SELECT ticker, end, revenue,
       LAG(revenue) OVER (PARTITION BY ticker ORDER BY end) AS prev_revenue,
       ROUND((revenue - LAG(revenue) OVER (PARTITION BY ticker ORDER BY end))
             / NULLIF(LAG(revenue) OVER (PARTITION BY ticker ORDER BY end), 0) * 100, 1) AS yoy_pct
FROM rev
ORDER BY ticker, end DESC;
