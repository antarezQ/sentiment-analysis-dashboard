"""Load and prepare the airline tweet data used by the dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Tweets.csv"
DASHBOARD_PATH = ROOT / "data" / "processed" / "dashboard_data.csv"

SENTIMENTS = ["negative", "neutral", "positive"]

# Only the columns the dashboard needs. User names, locations and
# coordinates from the original dataset are deliberately left out.
DASHBOARD_COLUMNS = [
    "tweet_id",
    "airline",
    "sentiment",
    "negative_reason",
    "tweet_created",
    "text",
]

AIRLINE_FIXES = {"Delta": "JetBlue"}

REASON_LABELS = {
    "longlines": "Long Lines",
}


def build_dashboard_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Turn the raw Kaggle `Tweets.csv` into the slim dashboard table."""
    df = raw.rename(
        columns={
            "airline_sentiment": "sentiment",
            "negativereason": "negative_reason",
        }
    )
    # 155 tweets appear twice; 18 of them with different labels. Keep the
    # copy whose sentiment label the annotators were most confident about.
    if "airline_sentiment_confidence" in df.columns:
        df = df.sort_values("airline_sentiment_confidence", ascending=False, kind="stable")
    df = df.drop_duplicates(subset="tweet_id")
    df = df[df["sentiment"].isin(SENTIMENTS)]

    # 99.8% of tweets labeled "Delta" in the source are addressed to
    # @JetBlue (only 0.3% mention @Delta), so the label is wrong.
    df["airline"] = df["airline"].replace(AIRLINE_FIXES)

    df["negative_reason"] = df["negative_reason"].replace(REASON_LABELS)
    # Reasons only make sense for negative tweets.
    df.loc[df["sentiment"] != "negative", "negative_reason"] = pd.NA

    # Timestamps look like "2015-02-24 11:35:52 -0800" (US Pacific time).
    created = pd.to_datetime(df["tweet_created"], utc=True)
    df["tweet_created"] = created.dt.tz_convert("US/Pacific").dt.tz_localize(None)

    df["text"] = df["text"].str.replace("&amp;", "&", regex=False)
    return df[DASHBOARD_COLUMNS].sort_values("tweet_created").reset_index(drop=True)


def load_dashboard_data(path: Path = DASHBOARD_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["tweet_created"])
    df["date"] = df["tweet_created"].dt.date
    df["hour"] = df["tweet_created"].dt.hour
    return df
