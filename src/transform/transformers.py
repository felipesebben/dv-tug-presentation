"""Transform-stage classes: join raw SIH/CNES parquet extracts into enriched/aggregated tables."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.transform import bed_type_crosswalk
from src.transform.dictionary_resolver import DictionaryResolver
from src.transform.duckdb_session import DuckDBSession

def geography_columns(include_id_municipio: bool = True) -> str:
    """Geography columns to carry from the municipio directory onto a fact table.

    The directory is the only source of these — none exist on the fact tables — and they
    are what makes a regional filter and a code-joined choropleth possible. Three
    granularities are carried because they answer different questions: regiao_saude (30
    in RS) is SUS's own planning unit and the one a state health analyst actually works
    in, regiao_intermediaria (8) is coarse enough to be a usable filter, and
    microrregiao (35) sits between them.

    ``nome_regiao`` is kept even though it is the constant "Sul" under a single-state
    scope, because V1's workbook binds to it in 18 places and V1 has to keep working —
    the talk shows V1 and V2 side by side against the same extract.

    Args:
        include_id_municipio: whether to select the directory's 7-digit code. False for
            tables that already carry their own ``id_municipio`` (leito does), since
            selecting both would produce a duplicate column name.
    """
    columns = [
        "m.nome AS nome_municipio",
        "m.nome_regiao",  # constant under RS scope; retained for V1 compatibility
        "m.nome_regiao_saude",
        "m.nome_regiao_intermediaria",
        "m.nome_microrregiao",
        "m.centroide",  # WKT POINT — a point-map fallback if the choropleth join fails
    ]
    if include_id_municipio:
        columns.insert(0, "m.id_municipio")
    return ",\n                ".join(columns)


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
    DATASUS municipality code rather than the 7-digit IBGE id_municipio. Picking
    m.id_municipio up from that join is what gives the record-level table the 7-digit
    code, so it can reach the IBGE geometry the same way the other tables do.
    """

    DICTIONARY_COLUMNS = [
        "tipo_aih",
        "carater_internacao",
        "motivo_saida",
        "complexidade",
        "especialidade_leito",
        "tipo_uti",
        "tipo_uci",
    ]

    @property
    def output_filename(self) -> str:
        return "aihs_enriched.parquet"

    def build_query(self) -> str:
        aihs_path = (self.raw_dir / "aihs_reduzidas.parquet").as_posix()
        dicionario_path = self.raw_dir / "br_ms_sih_dicionario.parquet"
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()
        resolver = DictionaryResolver(dicionario_path, self.DICTIONARY_COLUMNS)
        bed_type = bed_type_crosswalk.sql_case_expression("a.especialidade_leito")

        # No leito_covid column: the COVID-specific specialty codes are unused in RS
        # (verified zero rows), so the flag would be constant False — see
        # bed_type_crosswalk.COVID_BED_CODES.
        return f"""
            SELECT
                a.*,
                {resolver.select_fragment()},
                {bed_type} AS tipo_leito_cnes,
                {geography_columns()},
                m.sigla_uf,
                m.nome_uf
            FROM read_parquet('{aihs_path}') a
            {resolver.join_fragment('a')}
            LEFT JOIN read_parquet('{municipio_path}') m
                ON m.id_municipio_6 = a.id_municipio_estabelecimento
        """


class LeitoEnricher(BaseTransformer):
    """Enriches leito rows with dictionary descriptions and municipio geography.

    Also flags which "complementar" beds are genuinely intensive care. CNES's
    complementar category bundles ICU and coronary units together with intermediate-care
    and isolation beds, so without the flag any chart labelled "UTI" overstates intensive
    capacity by about a third.
    """

    DICTIONARY_COLUMNS = ["tipo_leito", "tipo_especialidade_leito"]

    @property
    def output_filename(self) -> str:
        return "leito_enriched.parquet"

    def build_query(self) -> str:
        leito_path = (self.raw_dir / "leito.parquet").as_posix()
        dicionario_path = self.raw_dir / "br_ms_cnes_dicionario.parquet"
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()
        resolver = DictionaryResolver(dicionario_path, self.DICTIONARY_COLUMNS)
        # The resolver aliases tipo_especialidade_leito's description as
        # tipo_especialidade_leito_desc, which is what the ICU test has to read.
        is_icu = bed_type_crosswalk.sql_is_icu_specialty(
            "d_tipo_especialidade_leito.valor"
        )

        return f"""
            SELECT
                l.*,
                {resolver.select_fragment()},
                {is_icu} AS leito_uti,
                {geography_columns(include_id_municipio=False)},
                m.nome_uf
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

    Intensive care is aggregated alongside the network-wide figures, at the same
    hospital/month grain, so an ICU rate can be drilled the same way. Its numerator is
    SIH's own ``quantidade_dias_uti_mes`` counter rather than anything derived from
    ``especialidade_leito``: ICU days are recorded independently of the specialty the
    admission was billed under, so a patient in a clinical bed who spends four days in
    intensive care contributes 4 ICU days while still counting as a clinical admission.
    The denominator is only the ICU/coronary subset of CNES's ``complementar`` beds —
    see ``bed_type_crosswalk``.

    Numerators and denominators are kept separate rather than pre-divided, for the same
    reason as in ``OccupancyRefiner``: a ratio cannot be re-aggregated.
    """

    LEITO_INPUT = "leito_enriched.parquet"

    @property
    def output_filename(self) -> str:
        return "occupancy.parquet"

    def leito_input_path(self) -> Path:
        """LeitoEnricher's output, which this transformer consumes instead of the raw
        extract because it needs the ``leito_uti`` flag to build the ICU denominator.

        The ordering requirement is checked rather than assumed. If it were left
        implicit, reordering run_transform.py would not raise — it would quietly emit an
        occupancy table whose ICU columns were missing, which is the kind of failure that
        survives all the way to a chart.
        """
        path = self.output_dir / self.LEITO_INPUT
        if not path.exists():
            raise FileNotFoundError(
                f"{self.__class__.__name__} needs {self.LEITO_INPUT}, which LeitoEnricher "
                f"writes. Expected it at {path} — run LeitoEnricher first."
            )
        return path

    def build_query(self) -> str:
        aihs_path = (self.raw_dir / "aihs_reduzidas.parquet").as_posix()
        leito_path = self.leito_input_path().as_posix()
        municipio_path = (self.raw_dir / "municipio.parquet").as_posix()

        return f"""
            WITH aihs_agg AS (
                SELECT
                    id_estabelecimento_cnes,
                    ano,
                    mes,
                    COUNT(*) AS total_internacoes,
                    SUM(quantidade_dias_permanencia) AS total_dias_permanencia,
                    SUM(quantidade_dias_uti_mes) AS dias_uti,
                    SUM(quantidade_dias_unidade_intermediaria) AS dias_uci,
                    SUM(valor_uti) AS valor_uti,
                    COUNT(*) FILTER (WHERE quantidade_dias_uti_mes > 0)
                        AS internacoes_com_uti
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
                    SUM(quantidade_sus) AS leitos_sus,
                    SUM(quantidade_sus) FILTER (WHERE leito_uti) AS leitos_uti_sus
                FROM read_parquet('{leito_path}')
                GROUP BY id_estabelecimento_cnes, ano, mes, sigla_uf, id_municipio
            )
            SELECT
                aihs_agg.id_estabelecimento_cnes,
                aihs_agg.ano,
                aihs_agg.mes,
                leito_agg.sigla_uf,
                {geography_columns()},
                m.nome_uf,
                aihs_agg.total_internacoes,
                aihs_agg.total_dias_permanencia,
                aihs_agg.dias_uti,
                aihs_agg.dias_uci,
                aihs_agg.valor_uti,
                aihs_agg.internacoes_com_uti,
                leito_agg.leitos_total,
                leito_agg.leitos_sus,
                leito_agg.leitos_uti_sus,
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
