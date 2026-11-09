"""The SQL analysis must give the same numbers as the dashboard (pandas)."""

import pandas as pd
import pytest

pytest.importorskip("duckdb")

from src import metrics  # noqa: E402
from src.data import RAW_PATH, load_dashboard_data  # noqa: E402
from src.sql import SQL_DIR, run_sql_file  # noqa: E402


@pytest.fixture(scope="module")
def data():
    return load_dashboard_data()


def test_every_sql_file_documents_question_and_how_to_run():
    for path in sorted(SQL_DIR.glob("*.sql")):
        header = path.read_text(encoding="utf-8")[:600]
        assert "Business question:" in header, path.name
        assert "How to run" in header, path.name


def test_sentiment_by_airline_matches_dashboard(data):
    sql = run_sql_file(SQL_DIR / "02_sentiment_by_airline.sql").set_index("airline")
    pandas = metrics.sentiment_share_by_airline(data)
    assert list(sql.index) == list(pandas.index)
    assert (sql["tweets"] == pandas["tweets"]).all()
    pd.testing.assert_series_equal(sql["negative_pct"], pandas["negative"].round(1), check_names=False)


def test_complaint_drivers_match_dashboard(data):
    sql = run_sql_file(SQL_DIR / "03_complaint_drivers.sql").set_index("reason")
    pandas = metrics.reason_share(data)
    assert sql["complaints"].sum() == pandas["tweets"].sum()
    for reason, row in pandas.iterrows():
        assert sql.loc[reason, "complaints"] == row["tweets"]
        assert sql.loc[reason, "reason_share_pct"] == pytest.approx(row["share"], abs=0.05)


def test_daily_trend_matches_dashboard(data):
    sql = run_sql_file(SQL_DIR / "05_daily_trend.sql")
    pandas = metrics.daily_negative_share(data)
    assert len(sql) == len(pandas)
    assert sql["tweets"].sum() == pandas["tweets"].sum()


def test_top_reasons_and_priorities_exclude_cant_tell():
    top = run_sql_file(SQL_DIR / "04_top_reason_per_airline.sql")
    assert (top.groupby("airline")["reason_rank"].max() == 2).all()
    priority = run_sql_file(SQL_DIR / "06_priority_matrix.sql")
    assert len(priority) == 10
    assert "Can't Tell" not in set(top["reason"]) | set(priority["reason"])


@pytest.mark.skipif(not RAW_PATH.exists(), reason="raw Tweets.csv is not committed")
def test_data_quality_counts_duplicates_removed_by_cleaning(data):
    quality = run_sql_file(SQL_DIR / "01_data_quality.sql")
    assert quality["rows"].sum() - quality["duplicate_rows"].sum() == len(data)
