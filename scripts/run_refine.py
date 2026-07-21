"""Finalizes transformed SIH/CNES tables and exports them into a single .hyper file
for Tableau, writing parquet checkpoints to data/refined/ along the way.

Runs entirely locally (DuckDB + pantab) — no BigQuery calls, no cost.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.refine.hyper_exporter import HyperExporter
from src.refine.refiners import HospitalizacoesRefiner, LeitosRefiner, OccupancyRefiner
from src.transform.duckdb_session import DuckDBSession

TRANSFORMED_DIR = Path(__file__).resolve().parents[1] / "data" / "transformed"
REFINED_DIR = Path(__file__).resolve().parents[1] / "data" / "refined"
HYPER_PATH = REFINED_DIR / "sih_cnes_rs.hyper"


def main() -> None:
    session = DuckDBSession()
    refiners = {
        "occupancy": OccupancyRefiner(session, TRANSFORMED_DIR, REFINED_DIR),
        "hospitalizacoes": HospitalizacoesRefiner(session, TRANSFORMED_DIR, REFINED_DIR),
        "leitos": LeitosRefiner(session, TRANSFORMED_DIR, REFINED_DIR),
    }

    tables = {}
    for name, refiner in refiners.items():
        output_path = refiner.run()
        print(f"Wrote {output_path}")
        tables[name] = session.query(f"SELECT * FROM read_parquet('{output_path.as_posix()}')")

    session.close()

    exporter = HyperExporter(HYPER_PATH)
    hyper_path = exporter.export(tables)
    print(f"Wrote {hyper_path}")


if __name__ == "__main__":
    main()
