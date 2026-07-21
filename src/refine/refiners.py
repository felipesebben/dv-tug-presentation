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
    """Finalizes the hospital/month occupancy table: adds a date column, rounds the rate."""

    @property
    def output_filename(self) -> str:
        return "occupancy.parquet"

    def build_query(self) -> str:
        occupancy_path = (self.transformed_dir / "occupancy.parquet").as_posix()
        return f"""
            SELECT
                id_estabelecimento_cnes,
                ano,
                mes,
                make_date(ano, mes, 1) AS ano_mes,
                sigla_uf,
                nome_municipio,
                nome_uf,
                nome_regiao,
                total_internacoes,
                total_dias_permanencia,
                leitos_total,
                leitos_sus,
                ROUND(taxa_ocupacao, 4) AS taxa_ocupacao
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
