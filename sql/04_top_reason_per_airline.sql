-- Business question: What are the #1 and #2 complaints for each airline, so each
-- airline knows what to fix first?
--
-- How to run (from the project root):
--   python scripts/run_sql.py sql/04_top_reason_per_airline.sql
--   or with the DuckDB CLI:  duckdb < sql/04_top_reason_per_airline.sql
--
-- "Can't Tell" is excluded: annotators could not identify a reason, so an airline
-- cannot act on it. Shares are of each airline's actionable complaints.

WITH tweets AS (
    SELECT * FROM read_csv_auto('data/processed/dashboard_data.csv')
),
counts AS (
    SELECT airline, negative_reason AS reason, COUNT(*) AS complaints
    FROM tweets
    WHERE sentiment = 'negative'
      AND negative_reason IS NOT NULL
      AND negative_reason <> 'Can''t Tell'
    GROUP BY airline, negative_reason
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY airline ORDER BY complaints DESC, reason)  AS reason_rank,
           ROUND(100.0 * complaints / SUM(complaints) OVER (PARTITION BY airline), 1) AS share_of_airline_pct
    FROM counts
)
SELECT airline, reason_rank, reason, complaints, share_of_airline_pct
FROM ranked
WHERE reason_rank <= 2
ORDER BY airline, reason_rank;
