"""Airline Twitter sentiment dashboard.

Run from the project root:
    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from src import metrics  # noqa: E402
from src.data import DASHBOARD_PATH, SENTIMENTS, load_dashboard_data  # noqa: E402

st.set_page_config(page_title="Airline Sentiment Dashboard", page_icon="✈️", layout="wide")

# Streamlit cuts long metric values with "…" on narrow screens. Let KPI text
# wrap and shrink with the window instead, so "Customer Service Issue" stays readable.
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] *,
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.3rem, 2.6vw, 2.25rem);
        line-height: 1.15;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sentiment is a polarity, so it uses a diverging pair: red / gray / blue.
SENTIMENT_COLORS = {"negative": "#e34948", "neutral": "#a8a79f", "positive": "#2a78d6"}
# Each airline keeps the same color in every chart, whatever the filter.
AIRLINE_COLORS = {
    "United": "#2a78d6",
    "US Airways": "#eb6834",
    "American": "#1baf7a",
    "Southwest": "#eda100",
    "JetBlue": "#e87ba4",
    "Virgin America": "#6250d6",
}
SEQUENTIAL_BLUE = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def style(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(namelength=-1),
    )
    fig.update_xaxes(showgrid=False)
    return fig


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_dashboard_data()


if not DASHBOARD_PATH.exists():
    st.error(
        "Dashboard data not found. Put `Tweets.csv` in `data/raw/` and run "
        "`python scripts/build_dashboard_data.py`."
    )
    st.stop()

data = get_data()

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Filters")
airlines = sorted(data["airline"].unique())
selected_airlines = st.sidebar.multiselect("Airline", airlines, default=airlines)
min_date, max_date = data["date"].min(), data["date"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_date, max_date

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: [Twitter US Airline Sentiment]"
    "(https://www.kaggle.com/datasets/crowdflower/twitter-airline-sentiment) "
    "(CrowdFlower, CC BY-NC-SA 4.0). Times are US Pacific."
)

df = data[data["airline"].isin(selected_airlines) & data["date"].between(start, end)]
if df.empty:
    st.warning("No tweets match the current filters.")
    st.stop()

# ---------------------------------------------------------------- header
st.title("✈️ Airline Sentiment on Twitter")
st.markdown(
    "Which US airlines do customers complain about most, **why** do they complain, "
    "and what should airlines fix first? Based on "
    f"{len(data):,} tweets from {min_date:%d %b} to {max_date:%d %b %Y}."
)

k = metrics.kpis(df)
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
c1.metric("Tweets", f"{k['tweets']:,}")
c2.metric("Negative", f"{k['negative_share']:.1%}")
c3.metric("Positive", f"{k['positive_share']:.1%}")
c4.metric(f"Top complaint ({k['top_reason_share']:.0%} of complaints)", k["top_reason"])

tab_rep, tab_why, tab_time, tab_tweets, tab_model = st.tabs(
    ["Airline reputation", "Why customers complain", "Over time", "Read the tweets", "Try the model"]
)

# ---------------------------------------------------------------- reputation
with tab_rep:
    share = metrics.sentiment_share_by_airline(df)
    worst, best = share.index[0], share.index[-1]
    if len(share) > 1:
        st.markdown(
            f"**{worst}** has the worst reputation: **{share.loc[worst, 'negative']:.1f}%** of its tweets "
            f"are negative, versus **{share.loc[best, 'negative']:.1f}%** for **{best}**."
        )
    long = share[SENTIMENTS].reset_index().melt(id_vars="airline", var_name="sentiment", value_name="share")
    long = long.merge(share["tweets"].reset_index(), on="airline")
    fig = px.bar(
        long,
        x="share",
        y="airline",
        color="sentiment",
        orientation="h",
        category_orders={"airline": list(share.index), "sentiment": SENTIMENTS},
        color_discrete_map=SENTIMENT_COLORS,
        custom_data=["sentiment", "tweets"],
        labels={"share": "Share of the airline's tweets (%)", "airline": ""},
    )
    fig.update_traces(
        marker_line_width=2,
        marker_line_color="rgba(0,0,0,0)",
        hovertemplate="%{y}<br>%{customdata[0]}: %{x:.1f}%<br>%{customdata[1]:,} tweets total<extra></extra>",
    )
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(style(fig), width="stretch", theme="streamlit")

    with st.expander("Table view"):
        st.dataframe(
            share.rename(columns=str.title).style.format({c.title(): "{:.1f}%" for c in SENTIMENTS} | {"Tweets": "{:,}"}),
            width="stretch",
        )

# ---------------------------------------------------------------- reasons
with tab_why:
    reasons = metrics.reason_share(df)
    if reasons.empty:
        st.info("No negative tweets in the current selection.")
    else:
        ops = reasons["share"].reindex(["Late Flight", "Cancelled Flight"]).fillna(0).sum()
        st.markdown(
            f"**{reasons.index[0]}** drives **{reasons['share'].iloc[0]:.1f}%** of complaints. "
            f"Delays and cancellations together account for **{ops:.1f}%**."
        )
        left, right = st.columns([2, 3])
        with left:
            st.subheader("Complaint reasons")
            r = reasons.reset_index(names="reason")
            fig = px.bar(
                r,
                x="share",
                y="reason",
                orientation="h",
                custom_data=["tweets"],
                labels={"share": "Share of negative tweets (%)", "reason": ""},
            )
            fig.update_traces(
                marker_color=SENTIMENT_COLORS["negative"],
                hovertemplate="%{y}: %{x:.1f}%<br>%{customdata[0]:,} tweets<extra></extra>",
            )
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_xaxes(ticksuffix="%")
            st.plotly_chart(style(fig, 420), width="stretch", theme="streamlit")
        with right:
            st.subheader("Complaint mix by airline")
            st.caption("Each row sums to 100% of that airline's complaints.")
            mix = metrics.reason_by_airline(df)
            fig = px.imshow(
                mix,
                text_auto=".0f",
                aspect="auto",
                color_continuous_scale=SEQUENTIAL_BLUE,
                labels={"x": "", "y": "", "color": "% of complaints"},
            )
            fig.update_traces(hovertemplate="%{y} · %{x}: %{z:.1f}%<extra></extra>")
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(style(fig, 420), width="stretch", theme="streamlit")

# ---------------------------------------------------------------- over time
with tab_time:
    daily = metrics.daily_negative_share(df)
    st.subheader("Share of negative tweets per day")
    fig = px.line(
        daily,
        x="date",
        y="negative_share",
        color="airline",
        markers=True,
        color_discrete_map=AIRLINE_COLORS,
        custom_data=["tweets"],
        labels={"negative_share": "Negative tweets (%)", "date": ""},
    )
    fig.update_traces(
        line_width=2,
        marker_size=8,
        hovertemplate="%{fullData.name}<br>%{x|%d %b}: %{y:.1f}% negative<br>%{customdata[0]:,} tweets<extra></extra>",
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(style(fig), width="stretch", theme="streamlit")
    st.caption(
        "Only days with at least 30 tweets for an airline are shown. The source data has gaps: "
        "nearly all American Airlines tweets are from 22 Feb onward, and 16 and 24 Feb are partial days."
    )

    st.subheader("When do people tweet? (hour of day, US Pacific)")
    hourly = metrics.hourly_volume(df)
    fig = px.bar(
        hourly,
        x="hour",
        y="tweets",
        color="sentiment",
        category_orders={"sentiment": SENTIMENTS},
        color_discrete_map=SENTIMENT_COLORS,
        labels={"hour": "Hour of day", "tweets": "Tweets"},
    )
    fig.update_traces(hovertemplate="%{x}:00 · %{y:,} tweets<extra>%{fullData.name}</extra>")
    fig.update_layout(barmode="stack", bargap=0.15)
    fig.update_xaxes(dtick=2)
    st.plotly_chart(style(fig, 320), width="stretch", theme="streamlit")

# ---------------------------------------------------------------- tweets
with tab_tweets:
    f1, f2, f3 = st.columns([1, 2, 2])
    sentiment_pick = f1.selectbox("Sentiment", ["all"] + SENTIMENTS, index=1)
    reason_options = sorted(df["negative_reason"].dropna().unique())
    reason_pick = f2.multiselect("Complaint reason", reason_options, disabled=sentiment_pick not in ("all", "negative"))
    search = f3.text_input("Search text", placeholder="e.g. refund, baggage, crew")

    view = df
    if sentiment_pick != "all":
        view = view[view["sentiment"] == sentiment_pick]
    if reason_pick:
        view = view[view["negative_reason"].isin(reason_pick)]
    if search:
        view = view[view["text"].str.contains(search, case=False, regex=False)]

    st.caption(f"{len(view):,} tweets match.")
    st.dataframe(
        view[["tweet_created", "airline", "sentiment", "negative_reason", "text"]].sort_values(
            "tweet_created", ascending=False
        ),
        column_config={
            "tweet_created": st.column_config.DatetimeColumn("Time", format="D MMM, HH:mm"),
            "airline": "Airline",
            "sentiment": "Sentiment",
            "negative_reason": "Reason",
            "text": st.column_config.TextColumn("Tweet", width="large"),
        },
        hide_index=True,
        width="stretch",
        height=460,
    )

# ---------------------------------------------------------------- model
with tab_model:
    st.markdown(
        "A Logistic Regression model trained on these tweets can tag new tweets automatically, so a "
        "social care team only reads the ones that need action. It is right about **78%** of the time "
        "on held-out tweets; neutral tweets are the hardest to tell apart."
    )
    text = st.text_area(
        "Write a tweet to an airline",
        value="@united my flight was delayed 3 hours and nobody at the gate could tell us anything",
    )
    if text.strip():
        from src.predict import predict

        label, scores = predict(text)
        st.markdown(f"Predicted sentiment: **{label}** ({scores[label]:.0%} confidence)")
        probs = pd.DataFrame({"sentiment": SENTIMENTS, "probability": [scores[s] * 100 for s in SENTIMENTS]})
        fig = px.bar(
            probs,
            x="probability",
            y="sentiment",
            color="sentiment",
            orientation="h",
            color_discrete_map=SENTIMENT_COLORS,
            category_orders={"sentiment": SENTIMENTS},
            labels={"probability": "Probability (%)", "sentiment": ""},
        )
        fig.update_traces(hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
        fig.update_layout(showlegend=False)
        fig.update_xaxes(range=[0, 100], ticksuffix="%")
        st.plotly_chart(style(fig, 200), width="stretch", theme="streamlit")
