-- Business question: What drives customer complaints: operations (delays,
-- cancellations) or customer service?
--
-- How to run (from the project root):
--   python scripts/run_sql.py sql/03_complaint_drivers.sql
--   or with the DuckDB CLI:  duckdb < sql/03_complaint_drivers.sql
--
-- Groups the 10 annotated complaint reasons into 5 business areas and shows each
-- reason's share of all complaints next to its area's total share.

WITH tweets AS (
    SELECT * FROM read_csv_auto('data/processed/dashboard_data.csv')
),
complaints AS (
    SELECT negative_reason AS reason,
           CASE
               WHEN negative_reason IN ('Customer Service Issue', 'Flight Attendant Complaints') THEN 'Service'
               WHEN negative_reason IN ('Late Flight', 'Cancelled Flight')                    THEN 'Operations'
               WHEN negative_reason IN ('Lost Luggage', 'Damaged Luggage')                    THEN 'Baggage'
               WHEN negative_reason IN ('Bad Flight', 'Flight Booking Problems', 'Long Lines') THEN 'Product & booking'
               ELSE 'Unclear'
           END AS area
    FROM tweets
    WHERE sentiment = 'negative'
      AND negative_reason IS NOT NULL
),
by_reason AS (
    SELECT area, reason, COUNT(*) AS complaints
    FROM complaints
    GROUP BY area, reason
)
SELECT area,
       ROUND(100.0 * SUM(complaints) OVER (PARTITION BY area) / SUM(complaints) OVER (), 1) AS area_share_pct,
       reason,
       complaints,
       ROUND(100.0 * complaints / SUM(complaints) OVER (), 1)                              AS reason_share_pct
FROM by_reason
ORDER BY area_share_pct DESC, complaints DESC;
