"""Thin wrapper around a local DuckDB connection for the transform stage."""

import duckdb
import pandas as pd


class DuckDBSession:
    """Manages an in-memory DuckDB connection for querying local parquet files."""

    def __init__(self) -> None:
        self._connection = duckdb.connect(database=":memory:")

    def query(self, query: str) -> pd.DataFrame:
        return self._connection.sql(query).df()

    def close(self) -> None:
        self._connection.close()
