"""Aggregations behind each dashboard chart, kept separate so they can be tested."""

from __future__ import annotations

import pandas as pd

from src.data import SENTIMENTS


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    negative = df[df["sentiment"] == "negative"]
    shares = df["sentiment"].value_counts(normalize=True)
    top_reason = negative["negative_reason"].value_counts()
    return {
        "tweets": total,
        "negative_share": float(shares.get("negative", 0.0)),
        "positive_share": float(shares.get("positive", 0.0)),
        "top_reason": top_reason.index[0] if len(top_reason) else "-",
        "top_reason_share": float(top_reason.iloc[0] / top_reason.sum()) if len(top_reason) else 0.0,
    }


def sentiment_share_by_airline(df: pd.DataFrame) -> pd.DataFrame:
    """Percent of each airline's tweets per sentiment, worst airline first."""
    table = pd.crosstab(df["airline"], df["sentiment"], normalize="index") * 100
    table = table.reindex(columns=SENTIMENTS, fill_value=0.0)
    table["tweets"] = df["airline"].value_counts()
    return table.sort_values("negative", ascending=False)


def reason_share(df: pd.DataFrame) -> pd.DataFrame:
    """Share of negative tweets per complaint reason, largest first."""
    reasons = df.loc[df["sentiment"] == "negative", "negative_reason"].dropna()
    counts = reasons.value_counts()
    return pd.DataFrame({"tweets": counts, "share": counts / counts.sum() * 100})


def reason_by_airline(df: pd.DataFrame) -> pd.DataFrame:
    """Percent of each airline's complaints per reason (rows sum to 100)."""
    negative = df[df["sentiment"] == "negative"].dropna(subset=["negative_reason"])
    table = pd.crosstab(negative["airline"], negative["negative_reason"], normalize="index") * 100
    order = negative["negative_reason"].value_counts().index
    return table[order]


def daily_negative_share(df: pd.DataFrame, min_tweets: int = 30) -> pd.DataFrame:
    """Negative share per airline per day, long format for line charts.

    Airline-days with fewer than `min_tweets` tweets are dropped: a share
    computed from one or two tweets is just noise (0% or 100%).
    """
    grouped = df.groupby(["date", "airline"])["sentiment"]
    out = grouped.agg(tweets="size", negative=lambda s: (s == "negative").sum()).reset_index()
    out["negative_share"] = out["negative"] / out["tweets"] * 100
    return out[out["tweets"] >= min_tweets].reset_index(drop=True)


def hourly_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Tweet count per hour of day (Pacific time) and sentiment."""
    out = df.groupby(["hour", "sentiment"]).size().rename("tweets").reset_index()
    return out
