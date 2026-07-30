"""Refine-stage classes: finalize transformed tables for Tableau consumption."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.transform.duckdb_session import DuckDBSession


class BaseRefiner(ABC):
    """Base class for a DuckDB step reading data/transformed parquet, writing data/refined."""

    def __init__(self, session: DuckDBSession, transformed_dir: Path, output_dir: Path) -> None:
        self.session = session
        self.transformed_dir = transformed_dir
        self.output_dir = output_dir

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Parquet filename this refiner writes to, relative to output_dir."""

    @abstractmethod
    def build_query(self) -> str:
        """Returns the SQL query this refiner runs against the transformed parquet files."""

    def run(self) -> Path:
        df = self.session.query(self.build_query())
        output_path = self.output_dir / self.output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        return output_path


class OccupancyRefiner(BaseRefiner):
    """Finalizes the hospital/month occupancy table.

    Adds a date column and persists the *components* of the occupancy rate, not just the
    rate itself. A pre-divided ratio cannot be re-aggregated: averaging one hospital-month
    rate with another weights a 3-bed unit the same as a 1.127-bed one. Exporting
    numerator and denominator separately lets Tableau compute
    ``SUM(dias) / SUM(leito_dias)``, which stays correct at every drill level (month,
    municipality, state) with no LOD expressions.

    Two denominators are exported:

    ``leito_dias_total``
        All beds. Pairs with ``taxa_ocupacao`` and reproduces what V1 shows.

    ``leito_dias_sus``
        SUS beds only (77% of the total). This is the correct denominator: the numerator
        is SIH-SUS patient-days, i.e. SUS admissions, so dividing by all beds measures SUS
        demand against capacity SUS patients cannot occupy. State-level rate moves from
        43,0% (all beds) to 55,8% (SUS-only).

    38 of 15.994 hospital-months report zero SUS beds. Both ``dias_permanencia_sus`` and
    ``leito_dias_sus`` are NULL on those rows so numerator and denominator drop out
    together — nulling only the denominator would inflate the rate.

    ``leito_dias_uti_sus``
        The same construction for intensive care: ICU/coronary SUS beds only, paired with
        ``dias_uti``. Most hospitals have no ICU at all, so this denominator is NULL far
        more often than the general one — which is correct, and is why the pairing matters.
        A hospital with ICU patients recorded but no registered ICU bed would otherwise
        divide by zero; a hospital with ICU beds and no ICU patients would otherwise pull
        an aggregate rate down as if it were at 0% rather than being absent from the
        question.

    ``taxa_ocupacao`` is kept unchanged so the V1 workbook keeps working against the same
    extract; V2 uses the ``_sus`` columns.
    """

    @property
    def output_filename(self) -> str:
        return "occupancy.parquet"

    def build_query(self) -> str:
        occupancy_path = (self.transformed_dir / "occupancy.parquet").as_posix()
        dias_no_mes = "day(last_day(make_date(ano, mes, 1)))"
        return f"""
            SELECT
                id_estabelecimento_cnes,
                ano,
                mes,
                make_date(ano, mes, 1) AS ano_mes,
                {dias_no_mes} AS dias_no_mes,
                sigla_uf,
                id_municipio,
                nome_municipio,
                nome_uf,
                nome_regiao,
                nome_regiao_saude,
                nome_regiao_intermediaria,
                nome_microrregiao,
                centroide,
                total_internacoes,
                total_dias_permanencia,
                leitos_total,
                leitos_sus,
                leitos_total * {dias_no_mes} AS leito_dias_total,
                CASE WHEN leitos_sus > 0
                     THEN leitos_sus * {dias_no_mes}
                END AS leito_dias_sus,
                CASE WHEN leitos_sus > 0
                     THEN total_dias_permanencia
                END AS dias_permanencia_sus,
                ROUND(taxa_ocupacao, 4) AS taxa_ocupacao,
                CASE WHEN leitos_sus > 0
                     THEN ROUND(
                         total_dias_permanencia * 1.0 / (leitos_sus * {dias_no_mes}), 4)
                END AS taxa_ocupacao_sus,
                -- Intensive care, same numerator/denominator discipline as above.
                leitos_uti_sus,
                internacoes_com_uti,
                valor_uti,
                CASE WHEN leitos_uti_sus > 0 THEN dias_uti END AS dias_uti,
                dias_uci,
                CASE WHEN leitos_uti_sus > 0
                     THEN leitos_uti_sus * {dias_no_mes}
                END AS leito_dias_uti_sus,
                CASE WHEN leitos_uti_sus > 0
                     THEN ROUND(dias_uti * 1.0 / (leitos_uti_sus * {dias_no_mes}), 4)
                END AS taxa_ocupacao_uti
            FROM read_parquet('{occupancy_path}')
        """


class HospitalizacoesRefiner(BaseRefiner):
    """Finalizes record-level hospitalization detail for demographic/diagnosis drill-downs."""

    @property
    def output_filename(self) -> str:
        return "hospitalizacoes.parquet"

    def build_query(self) -> str:
        aihs_path = (self.transformed_dir / "aihs_enriched.parquet").as_posix()
        return f"""
            SELECT
                *,
                make_date(ano, mes, 1) AS ano_mes
            FROM read_parquet('{aihs_path}')
        """


class LeitosRefiner(BaseRefiner):
    """Finalizes bed-capacity detail."""

    @property
    def output_filename(self) -> str:
        return "leitos.parquet"

    def build_query(self) -> str:
        leito_path = (self.transformed_dir / "leito_enriched.parquet").as_posix()
        return f"""
            SELECT
                *,
                make_date(ano, mes, 1) AS ano_mes
            FROM read_parquet('{leito_path}')
        """
