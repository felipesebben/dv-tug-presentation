"""Extracts SIH/CNES data for one state and year range into data/raw/ as parquet.

Defaults to a dry run (prints estimated bytes processed per query, executes nothing).
Pass --execute to actually run the queries and write parquet files.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract.bigquery_client import BigQuerySession
from src.extract.extractors import (
    AihsReduzidasExtractor,
    DictionaryExtractor,
    DirectoryExtractor,
    LeitoExtractor,
)

SIGLA_UF = "RS"
ID_UF = "43"
ANO_INICIO = 2019
ANO_FIM = 2023
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def build_extractors(session: BigQuerySession):
    return [
        AihsReduzidasExtractor(session, OUTPUT_DIR, id_uf=ID_UF, ano_inicio=ANO_INICIO, ano_fim=ANO_FIM),
        LeitoExtractor(session, OUTPUT_DIR, sigla_uf=SIGLA_UF, ano_inicio=ANO_INICIO, ano_fim=ANO_FIM),
        DictionaryExtractor(session, OUTPUT_DIR, dataset_id="br_ms_sih", id_tabelas=["aihs_reduzidas"]),
        DictionaryExtractor(session, OUTPUT_DIR, dataset_id="br_ms_cnes", id_tabelas=["leito"]),
        DirectoryExtractor(session, OUTPUT_DIR, table_id="municipio"),
        DirectoryExtractor(session, OUTPUT_DIR, table_id="uf"),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run the queries and write parquet files (default: dry run only).",
    )
    args = parser.parse_args()

    load_dotenv()
    project_id = os.environ["BD_BILLING_PROJECT_ID"]
    session = BigQuerySession(billing_project=project_id)
    extractors = build_extractors(session)

    total_bytes = 0
    for extractor in extractors:
        bytes_processed = extractor.estimate_bytes() or 0
        total_bytes += bytes_processed
        print(f"{extractor.output_filename}: {bytes_processed / 1e6:.2f} MB estimated")
    print(f"Total estimated: {total_bytes / 1e6:.2f} MB")

    if not args.execute:
        print("\nDry run only — no queries executed. Pass --execute to run for real.")
        return

    for extractor in extractors:
        output_path = extractor.run()
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
