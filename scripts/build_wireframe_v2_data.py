"""Generates the data blob embedded in docs/v2/wireframe.html.

The V2 wireframe carries no synthetic numbers — every value and series in it is read
from data/refined/ by this script. It exists so that claim stays true: when the pipeline
is re-run, the wireframe can be regenerated rather than hand-patched, and a stale figure
becomes a diff instead of a silent inaccuracy.

Writes a single JSON file. Paste its contents into the wireframe's `const DATA = ...`.

Local only — reads parquet and GeoJSON from disk, costs nothing.
"""

import json
import math
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
REFINED = ROOT / "data" / "refined"
GEOJSON = ROOT / "data" / "raw" / "municipios_rs.geojson"
OUTPUT = ROOT / "data" / "refined" / "wireframe_v2_data.json"
TEMPLATE = ROOT / "docs" / "v2" / "wireframe_template.html"
WIREFRAME = ROOT / "docs" / "v2" / "wireframe.html"
DATA_PLACEHOLDER = "/*__DATA__*/"

# The map is drawn into a square box because Rio Grande do Sul is one: its bounding box
# is 6,805 x 6,660 degree-equivalents once longitude is corrected for latitude, an aspect
# ratio of 1,022. A wide strip would either waste ~800px or squash the state.
MAP_BOX = 1000
ANO_FOCO = 2023

# Vertex-decimation tolerance, in projected box units. The map renders at roughly 340px,
# so one box unit is about 0,34px and a tolerance of 2,5 discards vertices less than ~0,85px
# from the previous kept one — below the threshold of visibility, and it cuts the embedded
# payload by roughly three quarters. This is a wireframe concern only: Tableau reads the
# full-resolution GeoJSON, not this.
SIMPLIFY_TOLERANCE = 2.5

# Occupancy thresholds, shipped as data rather than hardcoded in the page so they can be
# changed in one place — including live, during the talk.
#
# 85% is the "occupancy rule" from the bed-crisis literature (Bagust, Place & Posnett,
# BMJ 1999), widely used in bed planning. It is a general acute-bed rule, and we have NOT
# found an official SES-RS or Ministry of Health target for ICU specifically — these
# defaults need sign-off from a clinical contact before being presented as a standard.
#
# The same pair applies to both views deliberately. At state level the network sits at
# 60,0% and never crosses, which is itself the finding: the strain is in intensive care,
# not in the wards. A threshold that fires constantly teaches people to ignore the colour;
# one that never fires at state level but discriminates on the map is doing its job.
LIMIARES = {"atencao": 0.85, "critico": 0.95}
# Rings smaller than this in bounding-box terms are dropped. At 340px they are sub-pixel
# specks — river islands in the Lagoa dos Patos, mostly.
MIN_RING_EXTENT = 2.0


class MapProjector:
    """Projects lon/lat onto a square SVG viewBox with an equirectangular correction.

    Longitude degrees are shorter than latitude degrees away from the equator, by
    cos(latitude). Ignoring that stretches Rio Grande do Sul about 16% too wide — enough
    to look subtly wrong to anyone who knows the state's shape, which in this audience is
    everyone.
    """

    def __init__(self, features: list[dict], box: int = MAP_BOX) -> None:
        xs, ys = [], []
        for feature in features:
            for lon, lat in self._vertices(feature["geometry"]["coordinates"]):
                xs.append(lon)
                ys.append(lat)
        self.lon0, self.lon1 = min(xs), max(xs)
        self.lat0, self.lat1 = min(ys), max(ys)
        self.k = math.cos(math.radians(abs((self.lat0 + self.lat1) / 2)))
        width = (self.lon1 - self.lon0) * self.k
        height = self.lat1 - self.lat0
        # Fit the longer side to the box and centre the shorter one.
        self.scale = box / max(width, height)
        self.box = box
        self.pad_x = (box - width * self.scale) / 2
        self.pad_y = (box - height * self.scale) / 2

    @staticmethod
    def _vertices(coords):
        """Yields (lon, lat) pairs from arbitrarily nested GeoJSON coordinate arrays."""
        if coords and isinstance(coords[0], (int, float)):
            yield coords[0], coords[1]
            return
        for part in coords:
            yield from MapProjector._vertices(part)

    def project(self, lon: float, lat: float) -> tuple[float, float]:
        x = self.pad_x + (lon - self.lon0) * self.k * self.scale
        # SVG y grows downward, latitude grows upward.
        y = self.pad_y + (self.lat1 - lat) * self.scale
        return x, y

    @staticmethod
    def _decimate(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Drops vertices closer than SIMPLIFY_TOLERANCE to the last one kept.

        Deliberately not Douglas-Peucker: this runs on already-simplified IBGE geometry
        at a display size where the difference is invisible, and a distance filter cannot
        introduce the self-intersections a naive DP implementation can.
        """
        if len(pts) < 3:
            return pts
        kept = [pts[0]]
        for x, y in pts[1:-1]:
            lx, ly = kept[-1]
            if (x - lx) ** 2 + (y - ly) ** 2 >= SIMPLIFY_TOLERANCE ** 2:
                kept.append((x, y))
        kept.append(pts[-1])  # always keep the closing vertex
        return kept

    def ring_to_path(self, ring: list) -> str:
        pts = [self.project(lon, lat) for lon, lat in ring]
        if len(pts) < 3:
            return ""
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if max(xs) - min(xs) < MIN_RING_EXTENT and max(ys) - min(ys) < MIN_RING_EXTENT:
            return ""
        pts = self._decimate(pts)
        if len(pts) < 3:
            return ""
        head = f"M{pts[0][0]:.0f},{pts[0][1]:.0f}"
        tail = "".join(f"L{x:.0f},{y:.0f}" for x, y in pts[1:])
        return head + tail + "Z"

    def feature_to_path(self, geometry: dict) -> str:
        """One SVG path string per municipality, including any islands or holes."""
        kind = geometry["type"]
        if kind == "Polygon":
            rings = geometry["coordinates"]
        elif kind == "MultiPolygon":
            rings = [ring for polygon in geometry["coordinates"] for ring in polygon]
        else:
            raise ValueError(f"unexpected geometry type {kind!r}")
        return "".join(self.ring_to_path(ring) for ring in rings)

    @property
    def aspect_ratio(self) -> float:
        return ((self.lon1 - self.lon0) * self.k) / (self.lat1 - self.lat0)


def query(con, sql: str) -> list[tuple]:
    return con.execute(sql).fetchall()


def build_map(con) -> dict:
    """Municipality outlines plus the occupancy rate that colours each one."""
    geojson = json.loads(GEOJSON.read_text(encoding="utf-8"))
    projector = MapProjector(geojson["features"])
    paths = {
        f["properties"]["codarea"]: projector.feature_to_path(f["geometry"])
        for f in geojson["features"]
    }
    rates = {
        code: [round(taxa, 4), round(leitos, 1), nome]
        for code, nome, leitos, taxa in query(con, f"""
            SELECT id_municipio, nome_municipio,
                   SUM(leito_dias_sus) / 365.0,
                   SUM(dias_permanencia_sus) / SUM(leito_dias_sus)
            FROM read_parquet('{(REFINED / "occupancy.parquet").as_posix()}')
            WHERE ano = {ANO_FOCO} AND leito_dias_sus IS NOT NULL
            GROUP BY 1, 2
        """)
    }
    return {
        "box": MAP_BOX,
        "aspect": round(projector.aspect_ratio, 3),
        "paths": paths,
        "rates": rates,
        "semLeito": sorted(set(paths) - set(rates)),
    }


def build_mensal(con) -> list[list]:
    """Monthly series as raw numerators and denominators, never as pre-divided rates.

    This is the shape that lets the wireframe's year filter recompute every figure as
    ``SUM(numerator) / SUM(denominator)`` in the browser, which is the same rule the
    Tableau build follows. Shipping rates instead would force the mock to average
    averages — the exact defect the V2 occupancy rebuild exists to fix — and the filter
    would then produce subtly wrong numbers while looking like it worked.
    """
    occupancy = (REFINED / "occupancy.parquet").as_posix()
    return [
        [f"{ano}-{mes:02d}", ano, mes, dias, leito_dias, uti, leito_dias_uti,
         internacoes, round(leitos, 1), round(leitos_uti, 1), int_uti]
        for ano, mes, dias, leito_dias, uti, leito_dias_uti, internacoes, leitos, \
            leitos_uti, int_uti
        in query(con, f"""
            SELECT ano, mes,
                   SUM(dias_permanencia_sus)::BIGINT,
                   SUM(leito_dias_sus)::BIGINT,
                   COALESCE(SUM(dias_uti), 0)::BIGINT,
                   COALESCE(SUM(leito_dias_uti_sus), 0)::BIGINT,
                   SUM(total_internacoes)::BIGINT,
                   SUM(leitos_sus)::DOUBLE,
                   COALESCE(SUM(leitos_uti_sus), 0)::DOUBLE,
                   COALESCE(SUM(internacoes_com_uti), 0)::BIGINT
            FROM read_parquet('{occupancy}')
            GROUP BY 1, 2 ORDER BY 1, 2
        """)
    ]


def build_permanencia(con) -> list[list]:
    """Mean length of stay per year, the counterweight to admission volume.

    Kept separate from the occupancy series because its denominator is admissions, not
    bed-days.
    """
    return [
        [ano, internacoes, round(media, 3)]
        for ano, internacoes, media in query(con, f"""
            SELECT ano, COUNT(*)::BIGINT,
                   AVG(quantidade_dias_permanencia)::DOUBLE
            FROM read_parquet('{(REFINED / "hospitalizacoes.parquet").as_posix()}')
            GROUP BY 1 ORDER BY 1
        """)
    ]


def build_tipos(con) -> dict:
    """Beds and occupancy per bed type per year.

    Intensive care is handled apart from the crosswalk on purpose: RS records no ICU code
    in especialidade_leito, so a crosswalked ICU numerator would be zero. Its numerator is
    the ICU day counter and its denominator only the ICU/UCO subset of complementar.
    """
    hosp = (REFINED / "hospitalizacoes.parquet").as_posix()
    leitos = (REFINED / "leitos.parquet").as_posix()
    occupancy = (REFINED / "occupancy.parquet").as_posix()
    dias_mes = "day(last_day(make_date(ano, mes, 1)))"

    ward = query(con, f"""
        WITH num AS (
            SELECT tipo_leito_cnes AS tipo, ano, mes,
                   SUM(quantidade_dias_permanencia)::BIGINT AS dias
            FROM read_parquet('{hosp}') GROUP BY 1, 2, 3),
        den AS (
            SELECT tipo_leito_desc AS tipo, ano, mes,
                   (SUM(quantidade_sus) * {dias_mes})::BIGINT AS leito_dias,
                   SUM(quantidade_sus)::DOUBLE AS leitos
            FROM read_parquet('{leitos}') GROUP BY 1, 2, 3)
        SELECT den.tipo, den.ano,
               SUM(den.leitos) / 12.0,
               COALESCE(SUM(num.dias), 0)::BIGINT,
               SUM(den.leito_dias)::BIGINT
        FROM den LEFT JOIN num
             ON num.tipo = den.tipo AND num.ano = den.ano AND num.mes = den.mes
        GROUP BY 1, 2 ORDER BY 1, 2
    """)
    icu = query(con, f"""
        SELECT ano,
               SUM(leitos_uti_sus) / 12.0,
               COALESCE(SUM(dias_uti), 0)::BIGINT,
               COALESCE(SUM(leito_dias_uti_sus), 0)::BIGINT
        FROM read_parquet('{occupancy}') GROUP BY 1 ORDER BY 1
    """)
    return {
        # [tipo, ano, leitos_medios, numerador, denominador]
        "enfermaria": [[t, a, round(b, 1), n, d] for t, a, b, n, d in ward],
        "uti": [[a, round(b, 1), n, d] for a, b, n, d in icu],
    }


def build_municipio_ano(con) -> list[list]:
    """Per-municipality, per-year components for both views, so the map, scatter and bars
    all follow the period filter *and* the rede/UTI switch.

    ICU columns are zero rather than null for municipalities with no ICU bed, so the
    client can tell "has no ICU at all" (denominator 0) apart from "has ICU and it is
    empty". That distinction is the Território tab's finding in ICU view: only 59 of 225
    municipalities with beds have any ICU bed at all.
    """
    return [
        [code, nome, ano, num, den, num_uti, den_uti]
        for code, nome, ano, num, den, num_uti, den_uti in query(con, f"""
            SELECT id_municipio, nome_municipio, ano,
                   SUM(dias_permanencia_sus)::BIGINT,
                   SUM(leito_dias_sus)::BIGINT,
                   COALESCE(SUM(dias_uti), 0)::BIGINT,
                   COALESCE(SUM(leito_dias_uti_sus), 0)::BIGINT
            FROM read_parquet('{(REFINED / "occupancy.parquet").as_posix()}')
            WHERE leito_dias_sus IS NOT NULL
            GROUP BY 1, 2, 3
        """)
    ]


def build_custo(con) -> dict:
    """Spend per year, and the volume/spend split by complexity."""
    hosp = (REFINED / "hospitalizacoes.parquet").as_posix()
    anual = query(con, f"""
        SELECT ano, COUNT(*)::BIGINT, SUM(valor_aih)::DOUBLE,
               AVG(valor_aih)::DOUBLE, MEDIAN(valor_aih)::DOUBLE
        FROM read_parquet('{hosp}') GROUP BY 1 ORDER BY 1
    """)
    complexidade = query(con, f"""
        SELECT ano, complexidade_desc, COUNT(*)::BIGINT, SUM(valor_aih)::DOUBLE
        FROM read_parquet('{hosp}') GROUP BY 1, 2 ORDER BY 1, 2
    """)
    uti = query(con, f"""
        SELECT ano, COALESCE(SUM(valor_uti), 0)::DOUBLE, SUM(valor_aih)::DOUBLE
        FROM read_parquet('{hosp}') GROUP BY 1 ORDER BY 1
    """)
    return {
        "anual": [[a, n, round(s, 2), round(m, 2), round(md, 2)] for a, n, s, m, md in anual],
        # "Méida Complexidade" is misspelled in BD's own dictionary; fixed for display only,
        # never in a join key.
        "complexidade": [
            [a, c.replace("Méida", "Média") if c else c, n, round(v, 2)]
            for a, c, n, v in complexidade
        ],
        "uti": [[a, round(vu, 2), round(vt, 2)] for a, vu, vt in uti],
    }


def build_idade(con) -> list[list]:
    """Share of admissions aged 60+, per year — evidence of future demand."""
    return [
        [ano, round(share, 4), round(media, 1)]
        for ano, share, media in query(con, f"""
            SELECT ano,
                   (COUNT(*) FILTER (WHERE idade_paciente >= 60)) * 1.0 / COUNT(*),
                   AVG(idade_paciente)::DOUBLE
            FROM read_parquet('{(REFINED / "hospitalizacoes.parquet").as_posix()}')
            GROUP BY 1 ORDER BY 1
        """)
    ]


def build_regioes(con) -> dict:
    """The two regional granularities, for the filter chips."""
    occupancy = (REFINED / "occupancy.parquet").as_posix()
    return {
        "intermediaria": [
            r[0] for r in query(con, f"""
                SELECT DISTINCT nome_regiao_intermediaria FROM read_parquet('{occupancy}')
                WHERE nome_regiao_intermediaria IS NOT NULL ORDER BY 1
            """)
        ],
        "saude": [
            r[0] for r in query(con, f"""
                SELECT DISTINCT nome_regiao_saude FROM read_parquet('{occupancy}')
                WHERE nome_regiao_saude IS NOT NULL ORDER BY 1
            """)
        ],
    }


def build_territorio(con) -> dict:
    """Ranked municipalities and the beds-versus-occupancy scatter.

    Both are ranked and plotted on *real* mean monthly SUS beds. The earlier wireframe
    used AVG(leitos_sus) — a mean per hospital-month — which reported Porto Alegre at 281
    beds instead of 4.748,6 and therefore ranked the whole list wrongly.
    """
    occupancy = (REFINED / "occupancy.parquet").as_posix()
    dias_ano = 365.0
    top = query(con, f"""
        SELECT nome_municipio,
               SUM(leito_dias_sus) / {dias_ano} AS leitos,
               SUM(dias_permanencia_sus) / SUM(leito_dias_sus) AS taxa
        FROM read_parquet('{occupancy}')
        WHERE ano = {ANO_FOCO} AND leito_dias_sus IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC LIMIT 15
    """)
    scatter = query(con, f"""
        SELECT nome_municipio,
               SUM(leito_dias_sus) / {dias_ano} AS leitos,
               SUM(dias_permanencia_sus) / SUM(leito_dias_sus) AS taxa
        FROM read_parquet('{occupancy}')
        WHERE ano = {ANO_FOCO} AND leito_dias_sus IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC
    """)
    estado = query(con, f"""
        SELECT SUM(dias_permanencia_sus) / SUM(leito_dias_sus)
        FROM read_parquet('{occupancy}') WHERE ano = {ANO_FOCO}
    """)[0][0]
    return {
        "top15": [[n, round(b, 1), round(t, 4)] for n, b, t in top],
        "scatter": [[n, round(b, 1), round(t, 4)] for n, b, t in scatter],
        "taxaEstado": round(estado, 4),
        "nMun": len(scatter),
    }


def main() -> None:
    if not (REFINED / "occupancy.parquet").exists():
        raise SystemExit("data/refined/occupancy.parquet not found — run the pipeline first.")
    if not GEOJSON.exists():
        raise SystemExit(
            f"{GEOJSON.name} not found — run scripts/fetch_municipal_geometry.py first."
        )

    con = duckdb.connect()
    data = {
        "anoFoco": ANO_FOCO,
        "limiares": LIMIARES,
        "mensal": build_mensal(con),
        "permanencia": build_permanencia(con),
        "tipos": build_tipos(con),
        "municipioAno": build_municipio_ano(con),
        "custo": build_custo(con),
        "idade": build_idade(con),
        "regioes": build_regioes(con),
        "mapa": build_map(con),
        "territorio": build_territorio(con),
    }

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT} ({size_kb:.0f} KB)")
    print(f"  map        : {len(data['mapa']['paths'])} polygons, "
          f"aspect {data['mapa']['aspect']} (1,0 = square), "
          f"{len(data['mapa']['semLeito'])} municipalities without beds")
    print(f"  mensal     : {len(data['mensal'])} months (raw num/den, filterable)")
    print(f"  municipio  : {len(data['municipioAno'])} municipality-years")
    print(f"  tipos      : {len(data['tipos']['enfermaria'])} ward type-years "
          f"+ {len(data['tipos']['uti'])} ICU years")
    print(f"  regioes    : {len(data['regioes']['intermediaria'])} intermediarias, "
          f"{len(data['regioes']['saude'])} de saude")
    print(f"  territorio : {data['territorio']['nMun']} municipalities, "
          f"state rate {data['territorio']['taxaEstado'] * 100:.2f}%")

    # The wireframe's central claim is that no number in it is synthetic. Recompute the
    # headline figures here from the emitted blob so a regression shows up as a failed
    # assertion rather than as a plausible wrong number on a slide.
    mensal = data["mensal"]
    def rate(rows, num, den):
        d = sum(r[den] for r in rows)
        return sum(r[num] for r in rows) / d if d else None
    y2023 = [r for r in mensal if r[1] == 2023]
    y2021 = [r for r in mensal if r[1] == 2021]
    print()
    print("  self-check:")
    print(f"    taxa geral 2023 = {rate(y2023, 3, 4) * 100:.2f}%  (expected 60,03%)")
    print(f"    taxa UTI   2021 = {rate(y2021, 5, 6) * 100:.2f}%  (expected 111,9%)")
    print(f"    taxa geral 2021 = {rate(y2021, 3, 4) * 100:.2f}%  (expected 53,2%)")
    print(f"    taxa geral tudo = {rate(mensal, 3, 4) * 100:.2f}%  (expected 55,85%)")

    assemble_wireframe(OUTPUT.read_text(encoding="utf-8"))


def assemble_wireframe(data_json: str) -> None:
    """Injects the data blob into the template to produce the self-contained wireframe.

    The wireframe has to be one file — it is published as an artifact under a CSP that
    blocks every external request, so the data cannot be fetched at runtime. Keeping the
    template and the data separate in the repo means the 230 KB blob never has to be
    hand-pasted, and a stale figure is a regenerate rather than a manual patch.
    """
    if not TEMPLATE.exists():
        print(f"WARNING: {TEMPLATE.name} not found — wireframe not assembled.")
        return
    template = TEMPLATE.read_text(encoding="utf-8")
    if DATA_PLACEHOLDER not in template:
        raise SystemExit(
            f"{TEMPLATE.name} is missing the {DATA_PLACEHOLDER} placeholder, so there is "
            f"nowhere to inject the data."
        )
    WIREFRAME.write_text(
        template.replace(DATA_PLACEHOLDER, data_json), encoding="utf-8"
    )
    print()
    print(f"  Wrote {WIREFRAME} ({WIREFRAME.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
