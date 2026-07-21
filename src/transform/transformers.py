"""Transform-stage classes: join raw SIH/CNES parquet extracts into enriched/aggregated tables."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.transform.dictionary_resolver import DictionaryResolver
from src.transform.duckdb_session import DuckDBSession


class BaseTransformer(ABC):
    """Base class for a DuckDB transform step reading data/raw parquet, writing parquet output."""

    def __init__(self, session: DuckDBSession, raw_dir: Path, output_dir: Path) -> None:
        self.session = session
        self.raw_dir = raw_dir
        self.output_dir = output_dir

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Parquet filename this transformer writes to, relative to output_dir."""

    @abstractmethod
    def build_query(self) -> str:
        """Returns the SQL query this transformer runs against the raw parquet files."""

    def run(self) -> Path:
        df = self.session.query(self.build_query())
        output_path = self.output_dir / self.output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        return output_path


class AihsEnricher(BaseTransformer):
    """Enriches aihs_reduzidas rows with dictionary descriptions and municipio geography.

    Joins municipio on id_municipio_6, since aihs_reduzidas uses the legacy 6-digit
    DATASUS municipality code rather than the 7-digit IBGE id_municipio.
    """

    DICTIONARY_COLUMNS = ["tipo_aih", "carater_internacao", "motivo_saida", "complexidade"]

    @property
    def output_filename(self) -> str:
        return "aihs_enriched.parquet"

    def build_query(self) -> str:
        aihs_path = (self.raw_dir / "aihs_reduzidas.parquet").as_posix()
        dicionario_path = self.raw_dir / "br_ms_sih_dicionario.parquet"
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()
        resolver = DictionaryResolver(dicionario_path, self.DICTIONARY_COLUMNS)

        return f"""
            SELECT
                a.*,
                {resolver.select_fragment()},
                m.nome AS nome_municipio,
                m.sigla_uf,
                m.nome_uf,
                m.nome_regiao
            FROM read_parquet('{aihs_path}') a
            {resolver.join_fragment('a')}
            LEFT JOIN read_parquet('{municipio_path}') m
                ON m.id_municipio_6 = a.id_municipio_estabelecimento
        """


class LeitoEnricher(BaseTransformer):
    """Enriches leito rows with dictionary descriptions and municipio geography."""

    DICTIONARY_COLUMNS = ["tipo_leito", "tipo_especialidade_leito"]

    @property
    def output_filename(self) -> str:
        return "leito_enriched.parquet"

    def build_query(self) -> str:
        leito_path = (self.raw_dir / "leito.parquet").as_posix()
        dicionario_path = self.raw_dir / "br_ms_cnes_dicionario.parquet"
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()
        resolver = DictionaryResolver(dicionario_path, self.DICTIONARY_COLUMNS)

        return f"""
            SELECT
                l.*,
                {resolver.select_fragment()},
                m.nome AS nome_municipio,
                m.nome_uf,
                m.nome_regiao
            FROM read_parquet('{leito_path}') l
            {resolver.join_fragment('l')}
            LEFT JOIN read_parquet('{municipio_path}') m
                ON m.id_municipio = l.id_municipio
        """


class OccupancyCalculator(BaseTransformer):
    """Computes the SIH/CNES occupancy rate approximation at hospital/month grain.

    Occupancy rate = total bed-days used (sum of quantidade_dias_permanencia across
    admissions) / total bed-capacity for the month (bed count x days in month). This
    is DATASUS's documented approximation, not a true point-in-time occupancy rate.
    """

    @property
    def output_filename(self) -> str:
        return "occupancy.parquet"

    def build_query(self) -> str:
        aihs_path = (self.raw_dir / "aihs_reduzidas.parquet").as_posix()
        leito_path = (self.raw_dir / "leito.parquet").as_posix()
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()

        return f"""
            WITH aihs_agg AS (
                SELECT
                    id_estabelecimento_cnes,
                    ano,
                    mes,
                    COUNT(*) AS total_internacoes,
                    SUM(quantidade_dias_permanencia) AS total_dias_permanencia
                FROM read_parquet('{aihs_path}')
                GROUP BY id_estabelecimento_cnes, ano, mes
            ),
            leito_agg AS (
                SELECT
                    id_estabelecimento_cnes,
                    ano,
                    mes,
                    sigla_uf,
                    id_municipio,
                    SUM(quantidade_total) AS leitos_total,
                    SUM(quantidade_sus) AS leitos_sus
                FROM read_parquet('{leito_path}')
                GROUP BY id_estabelecimento_cnes, ano, mes, sigla_uf, id_municipio
            )
            SELECT
                aihs_agg.id_estabelecimento_cnes,
                aihs_agg.ano,
                aihs_agg.mes,
                leito_agg.sigla_uf,
                m.nome AS nome_municipio,
                m.nome_uf,
                m.nome_regiao,
                aihs_agg.total_internacoes,
                aihs_agg.total_dias_permanencia,
                leito_agg.leitos_total,
                leito_agg.leitos_sus,
                aihs_agg.total_dias_permanencia
                    / (leito_agg.leitos_total * day(last_day(make_date(aihs_agg.ano, aihs_agg.mes, 1))))
                    AS taxa_ocupacao
            FROM aihs_agg
            JOIN leito_agg
                ON aihs_agg.id_estabelecimento_cnes = leito_agg.id_estabelecimento_cnes
               AND aihs_agg.ano = leito_agg.ano
               AND aihs_agg.mes = leito_agg.mes
            LEFT JOIN read_parquet('{municipio_path}') m
                ON m.id_municipio = leito_agg.id_municipio
        """
