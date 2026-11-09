-- Business question: Which airline + complaint combinations should the Customer
-- Experience team fix first?
--
-- How to run (from the project root):
--   python scripts/run_sql.py sql/06_priority_matrix.sql
--   or with the DuckDB CLI:  duckdb < sql/06_priority_matrix.sql
--
-- For each airline and complaint reason:
--   complaints      number of negative tweets (size of the problem)
--   pct_of_all      share of ALL actionable complaints in the data (impact)
--   index_vs_peers  the reason's share of this airline's complaints divided by its
--                   share across all airlines. 1.5 = 50% more common than at other
--                   airlines, so it is an airline-specific problem, not an industry one.
-- "Can't Tell" is excluded (not actionable). Top 10 by number of complaints.

WITH tweets AS (
    SELECT * FROM read_csv_auto('data/processed/dashboard_data.csv')
),
complaints AS (
    SELECT airline, negative_reason AS reason
    FROM tweets
    WHERE sentiment = 'negative'
      AND negative_reason IS NOT NULL
      AND negative_reason <> 'Can''t Tell'
),
pair AS (
    SELECT airline, reason, COUNT(*) AS complaints
    FROM complaints
    GROUP BY airline, reason
),
airline_total AS (
    SELECT airline, COUNT(*) AS airline_complaints
    FROM complaints
    GROUP BY airline
),
reason_overall AS (
    SELECT reason, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS overall_share
    FROM complaints
    GROUP BY reason
)
SELECT p.airline,
       p.reason,
       p.complaints,
       ROUND(100.0 * p.complaints / SUM(p.complaints) OVER (), 1)             AS pct_of_all,
       ROUND(p.complaints * 1.0 / a.airline_complaints / r.overall_share, 2)  AS index_vs_peers
FROM pair AS p
JOIN airline_total  AS a USING (airline)
JOIN reason_overall AS r USING (reason)
ORDER BY p.complaints DESC
LIMIT 10;
