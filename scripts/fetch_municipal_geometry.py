"""Downloads Rio Grande do Sul's municipal boundaries from IBGE into data/raw/.

Free — this hits a public IBGE REST API, not BigQuery, so unlike run_extraction.py it
costs nothing and can be re-run at will.

The downloaded GeoJSON is what Tableau connects to as a spatial file for the Território
tab's choropleth, joined to the refined tables on the 7-digit IBGE municipality code.
"""

import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract.geometry import IbgeMunicipalGeometry

SIGLA_UF = "RS"
ID_UF = "43"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw"
MUNICIPIO_PARQUET = OUTPUT_DIR / "municipio.parquet"


def expected_codes() -> set[str] | None:
    """The municipality codes the geometry must cover, read from the BD directory.

    Returns None if the directory hasn't been extracted yet, which downgrades the
    validation to a structural check rather than blocking the download.
    """
    if not MUNICIPIO_PARQUET.exists():
        print(f"WARNING: {MUNICIPIO_PARQUET.name} not found — skipping the "
              f"code-coverage check. Run scripts/run_extraction.py first for the "
              f"full validation.")
        return None
    rows = duckdb.connect().execute(
        "SELECT id_municipio FROM read_parquet(?) WHERE sigla_uf = ?",
        [str(MUNICIPIO_PARQUET), SIGLA_UF],
    ).fetchall()
    return {r[0] for r in rows}


def main() -> None:
    codes = expected_codes()
    geometry = IbgeMunicipalGeometry(
        output_dir=OUTPUT_DIR, id_uf=ID_UF, sigla_uf=SIGLA_UF, quality="intermediaria"
    )
    print(f"Fetching {SIGLA_UF} municipal boundaries from IBGE "
          f"(quality: {geometry.quality})...")
    output_path = geometry.run(expected_codes=codes)
    size_kb = output_path.stat().st_size / 1024
    print(f"Wrote {output_path} ({size_kb:.0f} KB)")
    if codes:
        print(f"Validated: {len(codes)} municipality polygons, "
              f"codes match the BD directory exactly.")


if __name__ == "__main__":
    main()
