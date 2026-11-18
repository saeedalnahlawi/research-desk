-- bank_queries.sql — bank analysis (Arab Bank: FY2024, FY2025, H1 2026)
-- Needs the manual figures loaded first:
--   python3 scripts/load_manual.py --csv data/manual/arabbank_figures.csv
-- Run with:  python3 scripts/run_queries.py --sql sql/bank_queries.sql

.headers on
.mode column

-- Q1. Sanity check: what have you entered, by period?
SELECT period, COUNT(*) AS items_entered
FROM manual_figures
GROUP BY period, year, is_interim
ORDER BY year, is_interim;

-- Q2. The bank ratio panel — the table that goes into the note.
--     ROE and NIM are annualised for the interim; efficiency is a ratio of two flows, so it is not.
SELECT period, roe_pct, nim_on_assets_pct, efficiency_ratio_pct, cost_incl_ecl_pct,
       loans_to_deposits_pct, equity_to_assets_pct, npl_ratio_pct, car_pct
FROM bank_ratios
ORDER BY year, is_interim;

-- Q3. Movement in the ratios that matter most, period over period.
SELECT period, roe_pct,
       LAG(roe_pct) OVER (ORDER BY year, is_interim) AS roe_prev,
       ROUND(roe_pct - LAG(roe_pct) OVER (ORDER BY year, is_interim), 2) AS roe_change_pp,
       efficiency_ratio_pct,
       ROUND(efficiency_ratio_pct - LAG(efficiency_ratio_pct) OVER (ORDER BY year, is_interim), 1) AS efficiency_change_pp,
       npl_ratio_pct
FROM bank_ratios
ORDER BY year, is_interim;

-- Q4. Valuation: P/B and P/E. Needs share price (JOD), share count and the JOD/USD rate.
SELECT period, price_jod, shares_m, fx, market_cap_usd_m, pb_x, pe_x
FROM bank_multiples
ORDER BY year, is_interim;

-- Q5. What ROE does the market's P/B imply?
--     Sustainable growth: P/B = (ROE - g) / (COE - g)  ->  implied ROE = P/B * (COE - g) + g
--     Change the two assumptions and defend them in the note.
WITH assumptions AS (SELECT 0.16 AS coe, 0.04 AS g)
SELECT m.period, m.pb_x,
       ROUND(m.pb_x * (a.coe - a.g) + a.g, 3) AS implied_roe
FROM bank_multiples m CROSS JOIN assumptions a
ORDER BY m.year, m.is_interim;

-- Q6. Why a DCF on a bank misleads, demonstrated rather than asserted.
--     Interest expense is operating cost, not financing, so FCFF has no meaning here.
--     The gearing that would have to be modelled is regulated.
SELECT period,
       ROUND(MAX(CASE WHEN item = 'total_assets' THEN value END), 0) AS total_assets_m,
       ROUND(MAX(CASE WHEN item = 'total_equity' THEN value END), 0) AS equity_m,
       ROUND(MAX(CASE WHEN item = 'total_assets' THEN value END)
             / NULLIF(MAX(CASE WHEN item = 'total_equity' THEN value END), 0), 1) AS assets_to_equity_x
FROM manual_figures
GROUP BY period, year, is_interim
ORDER BY year, is_interim;

-- Q7. Arithmetic checks on what you typed. Any non-zero in the last column is a data-entry error.
SELECT period,
       MAX(CASE WHEN item = 'interest_income' THEN value END)     AS interest_income,
       MAX(CASE WHEN item = 'interest_expense' THEN value END)    AS interest_expense,
       MAX(CASE WHEN item = 'net_interest_income' THEN value END) AS reported_nii,
       ROUND(MAX(CASE WHEN item = 'interest_income' THEN value END)
             - MAX(CASE WHEN item = 'interest_expense' THEN value END)
             - MAX(CASE WHEN item = 'net_interest_income' THEN value END), 3) AS nii_difference
FROM manual_figures
GROUP BY period, year, is_interim
ORDER BY year, is_interim;

-- Q8. Our multiple versus the exchange's own published multiple.
--     The exchange's P/E is an external figure whose basis is not documented; it is recorded
--     in data/manual/ase_quotes.csv with its date and used as-is. Any gap is disclosed in the note,
--     not explained away.
SELECT q.quote_date, q.ticker,
       q.price_jod                                        AS ase_price_jod,
       q.pe_ase                                           AS pe_exchange,
       (SELECT ROUND(pe_x, 2) FROM bank_multiples
         ORDER BY year DESC, is_interim DESC LIMIT 1)      AS pe_model_latest,
       (SELECT ROUND(pb_x, 2) FROM bank_multiples
         ORDER BY year DESC, is_interim DESC LIMIT 1)      AS pb_model_latest,
       ROUND(q.pe_ase - (SELECT pe_x FROM bank_multiples
         ORDER BY year DESC, is_interim DESC LIMIT 1), 2)  AS pe_gap
FROM ase_quotes q;
