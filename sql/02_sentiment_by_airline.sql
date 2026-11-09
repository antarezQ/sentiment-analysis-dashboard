-- Business question: Which airlines have the worst and best reputation on Twitter?
--
-- How to run (from the project root):
--   python scripts/run_sql.py sql/02_sentiment_by_airline.sql
--   or with the DuckDB CLI:  duckdb < sql/02_sentiment_by_airline.sql
--
-- Uses the cleaned data (duplicates removed, airline labels fixed).
-- net_sentiment_pp = positive share minus negative share, in percentage points.

WITH tweets AS (
    SELECT * FROM read_csv_auto('data/processed/dashboard_data.csv')
),
by_airline AS (
    SELECT airline,
           COUNT(*)                                        AS tweets,
           COUNT(*) FILTER (WHERE sentiment = 'negative')  AS negative,
           COUNT(*) FILTER (WHERE sentiment = 'neutral')   AS neutral,
           COUNT(*) FILTER (WHERE sentiment = 'positive')  AS positive
    FROM tweets
    GROUP BY airline
)
SELECT RANK() OVER (ORDER BY negative * 1.0 / tweets DESC)  AS rank_worst_first,
       airline,
       tweets,
       ROUND(100.0 * negative / tweets, 1)                  AS negative_pct,
       ROUND(100.0 * neutral  / tweets, 1)                  AS neutral_pct,
       ROUND(100.0 * positive / tweets, 1)                  AS positive_pct,
       ROUND(100.0 * (positive - negative) / tweets, 1)     AS net_sentiment_pp,
       ROUND(100.0 * negative / SUM(negative) OVER (), 1)   AS share_of_all_negative_pct
FROM by_airline
ORDER BY rank_worst_first;
