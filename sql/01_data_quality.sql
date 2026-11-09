-- Business question: Can we trust the raw data? Are tweets duplicated, and does
-- each tweet's airline label match the airline it is actually addressed to?
--
-- How to run (from the project root, needs data/raw/Tweets.csv from Kaggle):
--   python scripts/run_sql.py sql/01_data_quality.sql
--   or with the DuckDB CLI:  duckdb < sql/01_data_quality.sql
--
-- Reads the RAW file, before any cleaning. One row per airline label in the source.

WITH raw AS (
    SELECT * FROM read_csv_auto('data/raw/Tweets.csv')
),
duplicate_ids AS (
    -- tweet_ids that appear more than once, and whether their copies disagree
    SELECT tweet_id,
           ANY_VALUE(airline)                     AS airline,
           COUNT(*)                               AS copies,
           COUNT(DISTINCT airline_sentiment) > 1  AS conflicting_labels
    FROM raw
    GROUP BY tweet_id
    HAVING COUNT(*) > 1
),
duplicates_per_airline AS (
    SELECT airline,
           CAST(SUM(copies - 1) AS INTEGER)            AS duplicate_rows,
           COUNT(*) FILTER (WHERE conflicting_labels)  AS conflicting_ids
    FROM duplicate_ids
    GROUP BY airline
)
SELECT r.airline                                                                        AS source_label,
       COUNT(*)                                                                         AS rows,
       ANY_VALUE(COALESCE(d.duplicate_rows, 0))                                         AS duplicate_rows,
       ANY_VALUE(COALESCE(d.conflicting_ids, 0))                                        AS ids_with_conflicting_labels,
       ROUND(100.0 * COUNT(*) FILTER (WHERE r.text ILIKE '%@jetblue%') / COUNT(*), 1)  AS pct_mentioning_jetblue,
       ROUND(100.0 * COUNT(*) FILTER (WHERE r.text ILIKE '%@delta%')   / COUNT(*), 1)  AS pct_mentioning_delta
FROM raw AS r
LEFT JOIN duplicates_per_airline AS d USING (airline)
GROUP BY r.airline
ORDER BY rows DESC;
