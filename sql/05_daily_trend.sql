-- Business question: Is sentiment getting better or worse from day to day, and
-- which day was worst for each airline?
--
-- How to run (from the project root):
--   python scripts/run_sql.py sql/05_daily_trend.sql
--   or with the DuckDB CLI:  duckdb < sql/05_daily_trend.sql
--
-- Airline-days with fewer than 30 tweets are dropped (same rule as the dashboard):
-- a share from a handful of tweets is noise. Times are US Pacific.
-- change_pp = change in negative share vs the airline's previous day shown.

WITH tweets AS (
    SELECT * FROM read_csv_auto('data/processed/dashboard_data.csv')
),
daily AS (
    SELECT airline,
           CAST(tweet_created AS DATE)                                       AS day,
           COUNT(*)                                                          AS tweets,
           100.0 * COUNT(*) FILTER (WHERE sentiment = 'negative') / COUNT(*) AS negative_pct
    FROM tweets
    GROUP BY airline, CAST(tweet_created AS DATE)
    HAVING COUNT(*) >= 30
)
SELECT airline,
       day,
       tweets,
       ROUND(negative_pct, 1)                                                              AS negative_pct,
       ROUND(negative_pct - LAG(negative_pct) OVER (PARTITION BY airline ORDER BY day), 1) AS change_pp,
       RANK() OVER (PARTITION BY airline ORDER BY negative_pct DESC)                       AS worst_day_rank
FROM daily
ORDER BY airline, day;
