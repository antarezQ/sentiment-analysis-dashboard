"""Run one or more SQL files from sql/ with DuckDB and print the results.

Run from the project root:
    python scripts/run_sql.py sql/02_sentiment_by_airline.sql
    python scripts/run_sql.py sql/*.sql
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sql import run_sql_file  # noqa: E402


def main(paths: list[str]) -> None:
    if not paths:
        sys.exit(__doc__)
    for path in paths:
        print(f"\n=== {path} ===")
        print(run_sql_file(path).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1:])
