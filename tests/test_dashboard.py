import pandas as pd
import pytest

from src import metrics
from src.data import DASHBOARD_COLUMNS, build_dashboard_data
from src.predict import clean_text, predict


@pytest.fixture
def raw():
    return pd.DataFrame(
        {
            "tweet_id": [1, 2, 3, 4, 4],
            "airline_sentiment": ["negative", "negative", "positive", "neutral", "neutral"],
            "negativereason": ["Late Flight", "longlines", None, "Bad Flight", "Bad Flight"],
            "airline": ["United", "United", "Delta", "Delta", "Delta"],
            "name": ["a", "b", "c", "d", "d"],
            "tweet_location": ["NY", None, None, None, None],
            "tweet_created": [
                "2015-02-24 11:35:52 -0800",
                "2015-02-24 23:10:00 -0800",
                "2015-02-23 08:00:00 -0800",
                "2015-02-23 09:00:00 -0800",
                "2015-02-23 09:00:00 -0800",
            ],
            "text": ["@united late &amp; rude", "@united line", "@JetBlue thanks", "@JetBlue ok", "@JetBlue ok"],
        }
    )


@pytest.fixture
def prepared(raw):
    df = build_dashboard_data(raw)
    df["date"] = df["tweet_created"].dt.date
    df["hour"] = df["tweet_created"].dt.hour
    return df


def test_build_keeps_only_dashboard_columns_and_drops_duplicates(raw):
    df = build_dashboard_data(raw)
    assert list(df.columns) == DASHBOARD_COLUMNS
    assert df["tweet_id"].is_unique and len(df) == 4


def test_build_relabels_delta_as_jetblue(raw):
    assert set(build_dashboard_data(raw)["airline"]) == {"United", "JetBlue"}


def test_build_keeps_most_confident_duplicate():
    raw = pd.DataFrame(
        {
            "tweet_id": [7, 7],
            "airline_sentiment": ["neutral", "negative"],
            "airline_sentiment_confidence": [0.4, 0.9],
            "negativereason": [None, "Bad Flight"],
            "airline": ["United", "United"],
            "tweet_created": ["2015-02-24 11:35:52 -0800"] * 2,
            "text": ["x", "x"],
        }
    )
    assert build_dashboard_data(raw)["sentiment"].tolist() == ["negative"]


def test_build_cleans_reasons_text_and_time(raw):
    df = build_dashboard_data(raw).set_index("tweet_id")
    assert df.loc[2, "negative_reason"] == "Long Lines"
    assert pd.isna(df.loc[4, "negative_reason"])  # reason dropped for non-negative tweet
    assert df.loc[1, "text"] == "@united late & rude"
    assert df.loc[2, "tweet_created"].hour == 23  # stays in Pacific time


def test_sentiment_share_rows_sum_to_100_and_worst_first(prepared):
    share = metrics.sentiment_share_by_airline(prepared)
    assert share.index[0] == "United"
    assert share[["negative", "neutral", "positive"]].sum(axis=1).round(6).eq(100).all()


def test_reason_metrics(prepared):
    reasons = metrics.reason_share(prepared)
    assert reasons["share"].sum() == pytest.approx(100)
    mix = metrics.reason_by_airline(prepared)
    assert mix.loc["United"].sum() == pytest.approx(100)


def test_daily_share_drops_thin_days(prepared):
    # Fixture: United has 2 tweets on 24 Feb, JetBlue 2 on 23 Feb.
    assert len(metrics.daily_negative_share(prepared, min_tweets=2)) == 2
    assert metrics.daily_negative_share(prepared, min_tweets=3).empty


def test_kpis(prepared):
    k = metrics.kpis(prepared)
    assert k["tweets"] == 4
    assert k["negative_share"] == pytest.approx(0.5)


def test_clean_text_matches_notebook_pipeline():
    assert clean_text("@VirginAmerica WHAT a flight!!! http://t.co/x #late &amp; :(") == "what a flight late and"


def test_model_predicts_obvious_cases():
    assert predict("worst airline ever, delayed 5 hours and lost my bag")[0] == "negative"
    label, scores = predict("thank you so much, great crew and amazing service")
    assert label == "positive"
    assert sum(scores.values()) == pytest.approx(1)
