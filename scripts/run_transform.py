"""Joins raw SIH/CNES parquet extracts into enriched detail tables plus the
occupancy rate aggregate, writing everything to data/transformed/.

Runs entirely locally against data/raw/ via DuckDB — no BigQuery calls, no cost.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.transform.duckdb_session import DuckDBSession
from src.transform.transformers import AihsEnricher, LeitoEnricher, OccupancyCalculator

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "transformed"


def main() -> None:
    session = DuckDBSession()
    transformers = [
        AihsEnricher(session, RAW_DIR, OUTPUT_DIR),
        LeitoEnricher(session, RAW_DIR, OUTPUT_DIR),
        OccupancyCalculator(session, RAW_DIR, OUTPUT_DIR),
    ]
    for transformer in transformers:
        output_path = transformer.run()
        print(f"Wrote {output_path}")
    session.close()


if __name__ == "__main__":
    main()
