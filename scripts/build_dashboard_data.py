"""Build data/processed/dashboard_data.csv from data/raw/Tweets.csv.

Usage:
    python scripts/build_dashboard_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.data import DASHBOARD_PATH, RAW_PATH, build_dashboard_data  # noqa: E402


def main() -> None:
    if not RAW_PATH.exists():
        sys.exit(
            f"Missing {RAW_PATH}. Download Tweets.csv from "
            "https://www.kaggle.com/datasets/crowdflower/twitter-airline-sentiment"
        )
    raw = pd.read_csv(RAW_PATH)
    df = build_dashboard_data(raw)
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DASHBOARD_PATH, index=False)
    print(f"Wrote {len(df):,} rows ({len(raw) - len(df)} dropped) to {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()
