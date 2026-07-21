"""Extractor classes for pulling SIH/CNES fact and dimension tables from BigQuery."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.extract.bigquery_client import BigQuerySession


class BigQueryExtractor(ABC):
    """Base class for extracting a single BigQuery table into a local parquet file."""

    def __init__(self, session: BigQuerySession, output_dir: Path) -> None:
        self.session = session
        self.output_dir = output_dir

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Parquet filename this extractor writes to, relative to output_dir."""

    @abstractmethod
    def build_query(self) -> str:
        """Returns the SQL query this extractor runs."""

    def estimate_bytes(self) -> int:
        return self.session.estimate_bytes(self.build_query())

    def extract(self) -> pd.DataFrame:
        return self.session.query(self.build_query())

    @staticmethod
    def _normalize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Converts BigQuery DATE columns from pandas-gbq's 'dbdate' extension dtype
        to plain datetime64, so the saved parquet doesn't require importing db_dtypes
        just to be read back with pandas."""
        date_columns = [c for c in df.columns if df[c].dtype.name == "dbdate"]
        for column in date_columns:
            df[column] = pd.to_datetime(df[column])
        return df

    def run(self) -> Path:
        """Extracts and saves the table, returning the output path."""
        df = self._normalize_dtypes(self.extract())
        output_path = self.output_dir / self.output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        return output_path


class AihsReduzidasExtractor(BigQueryExtractor):
    """Extracts SIH hospitalization records (br_ms_sih.aihs_reduzidas) for one UF and year range.

    aihs_reduzidas.sigla_uf is unpopulated (NULL) in this table, so state scope is
    filtered via the first two digits of id_municipio_estabelecimento, which match
    the UF's id_uf code (e.g. '43' for Rio Grande do Sul) instead.
    """

    COLUMNS = [
        "ano",
        "mes",
        "id_estabelecimento_cnes",
        "id_municipio_estabelecimento",
        "data_internacao",
        "data_saida",
        "quantidade_dias_permanencia",
        "tipo_aih",
        "carater_internacao",
        "motivo_saida",
        "complexidade",
        "sexo_paciente",
        "idade_paciente",
        "raca_cor_paciente",
        "indicador_obito",
        "valor_aih",
    ]

    def __init__(
        self,
        session: BigQuerySession,
        output_dir: Path,
        id_uf: str,
        ano_inicio: int,
        ano_fim: int,
    ) -> None:
        super().__init__(session, output_dir)
        self.id_uf = id_uf
        self.ano_inicio = ano_inicio
        self.ano_fim = ano_fim

    @property
    def output_filename(self) -> str:
        return "aihs_reduzidas.parquet"

    def build_query(self) -> str:
        columns = ",\n            ".join(self.COLUMNS)
        return f"""
            SELECT
            {columns}
            FROM `basedosdados.br_ms_sih.aihs_reduzidas`
            WHERE ano BETWEEN {self.ano_inicio} AND {self.ano_fim}
              AND SUBSTR(id_municipio_estabelecimento, 1, 2) = '{self.id_uf}'
        """


class LeitoExtractor(BigQueryExtractor):
    """Extracts CNES bed-capacity records (br_ms_cnes.leito) for one state and year range."""

    def __init__(
        self,
        session: BigQuerySession,
        output_dir: Path,
        sigla_uf: str,
        ano_inicio: int,
        ano_fim: int,
    ) -> None:
        super().__init__(session, output_dir)
        self.sigla_uf = sigla_uf
        self.ano_inicio = ano_inicio
        self.ano_fim = ano_fim

    @property
    def output_filename(self) -> str:
        return "leito.parquet"

    def build_query(self) -> str:
        return f"""
            SELECT *
            FROM `basedosdados.br_ms_cnes.leito`
            WHERE ano BETWEEN {self.ano_inicio} AND {self.ano_fim}
              AND sigla_uf = '{self.sigla_uf}'
        """


class DictionaryExtractor(BigQueryExtractor):
    """Extracts the code -> description dictionary for a dataset, scoped to given tables."""

    def __init__(
        self,
        session: BigQuerySession,
        output_dir: Path,
        dataset_id: str,
        id_tabelas: list[str],
    ) -> None:
        super().__init__(session, output_dir)
        self.dataset_id = dataset_id
        self.id_tabelas = id_tabelas

    @property
    def output_filename(self) -> str:
        return f"{self.dataset_id}_dicionario.parquet"

    def build_query(self) -> str:
        tabelas = ", ".join(f"'{t}'" for t in self.id_tabelas)
        return f"""
            SELECT id_tabela, nome_coluna, chave, valor
            FROM `basedosdados.{self.dataset_id}.dicionario`
            WHERE id_tabela IN ({tabelas})
        """


class DirectoryExtractor(BigQueryExtractor):
    """Extracts a full BD directory/dimension table (e.g. municipio, uf) — small, unfiltered."""

    def __init__(self, session: BigQuerySession, output_dir: Path, table_id: str) -> None:
        super().__init__(session, output_dir)
        self.table_id = table_id

    @property
    def output_filename(self) -> str:
        return f"{self.table_id}.parquet"

    def build_query(self) -> str:
        return f"SELECT * FROM `basedosdados.br_bd_diretorios_brasil.{self.table_id}`"
