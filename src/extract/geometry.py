"""Municipal boundary geometry from IBGE, for the choropleth map.

Separate from the BigQuery extractors because the source is a public REST API rather
than a billed warehouse query — but it belongs to the same pipeline stage, so it lands
in data/raw/ alongside them and follows the same run()-returns-a-path contract.

Why ship our own geometry instead of leaning on Tableau's built-in geocoding: Tableau
matches place names, and 38 Rio Grande do Sul municipality names are also used by
municipalities in other states (Alto Alegre exists in RR and SP, Bom Jesus in PB, SC,
PI and RN). Name matching would silently mis-place or drop those. IBGE's polygons carry
the 7-digit IBGE code, which joins exactly to id_municipio, so the map is deterministic.
"""

import json
from pathlib import Path

import requests


class IbgeMunicipalGeometry:
    """Downloads one state's municipal boundaries from IBGE's malhas territoriais API.

    The API returns a GeoJSON FeatureCollection with one polygon per municipality,
    keyed on `codarea` — the 7-digit IBGE code. Tableau reads GeoJSON as a spatial
    file directly, so no conversion step is needed.
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/{id_uf}"
    # The API rejects numeric quality values with a 400; only these three names work.
    QUALITIES = ("minima", "intermediaria", "maxima")
    CODE_PROPERTY = "codarea"

    def __init__(
        self,
        output_dir: Path,
        id_uf: str,
        sigla_uf: str,
        quality: str = "intermediaria",
        timeout: int = 120,
    ) -> None:
        if quality not in self.QUALITIES:
            raise ValueError(f"quality must be one of {self.QUALITIES}, got {quality!r}")
        self.output_dir = output_dir
        self.id_uf = id_uf
        self.sigla_uf = sigla_uf
        self.quality = quality
        self.timeout = timeout

    @property
    def output_filename(self) -> str:
        return f"municipios_{self.sigla_uf.lower()}.geojson"

    def build_url(self) -> str:
        return self.BASE_URL.format(id_uf=self.id_uf)

    def build_params(self) -> dict[str, str]:
        return {
            "formato": "application/vnd.geo+json",
            "intrarregiao": "municipio",
            "qualidade": self.quality,
        }

    def fetch(self) -> dict:
        response = requests.get(
            self.build_url(), params=self.build_params(), timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def codes(self, geojson: dict) -> set[str]:
        """The set of municipality codes the geometry covers."""
        return {f["properties"][self.CODE_PROPERTY] for f in geojson["features"]}

    def validate(self, geojson: dict, expected_codes: set[str] | None = None) -> None:
        """Fails loudly on a geometry file that would produce a wrong map.

        A choropleth that silently drops municipalities looks finished, which is why
        this is an assertion and not a warning.
        """
        if geojson.get("type") != "FeatureCollection":
            raise ValueError(f"expected a FeatureCollection, got {geojson.get('type')!r}")
        features = geojson.get("features") or []
        if not features:
            raise ValueError("geometry has no features")

        missing_code = [
            i for i, f in enumerate(features)
            if not f.get("properties", {}).get(self.CODE_PROPERTY)
        ]
        if missing_code:
            raise ValueError(
                f"{len(missing_code)} feature(s) lack a {self.CODE_PROPERTY} property, "
                f"so they cannot be joined to the data"
            )

        if expected_codes is not None:
            found = self.codes(geojson)
            if found != expected_codes:
                raise ValueError(
                    f"geometry does not match the municipality directory: "
                    f"{len(expected_codes - found)} expected code(s) have no polygon, "
                    f"{len(found - expected_codes)} polygon(s) are not in the directory"
                )

    def run(self, expected_codes: set[str] | None = None) -> Path:
        """Fetches, validates and saves the geometry, returning the output path."""
        geojson = self.fetch()
        self.validate(geojson, expected_codes)
        output_path = self.output_dir / self.output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(geojson, handle, ensure_ascii=False)
        return output_path
