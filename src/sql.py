"""Run the analysis queries in sql/ with DuckDB.

The .sql files read CSVs by paths relative to the project root, so queries are
always run from there. DuckDB is a notebook/analysis dependency only; the
dashboard does not import this module.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from src.data import ROOT

SQL_DIR = ROOT / "sql"


def run_sql_file(path: str | Path) -> pd.DataFrame:
    import duckdb

    path = Path(path)
    if not path.is_absolute():
        path = (Path.cwd() / path) if (Path.cwd() / path).exists() else ROOT / path
    query = path.read_text(encoding="utf-8")
    cwd = Path.cwd()
    os.chdir(ROOT)
    try:
        with duckdb.connect() as con:
            return con.sql(query).df()
    finally:
        os.chdir(cwd)
