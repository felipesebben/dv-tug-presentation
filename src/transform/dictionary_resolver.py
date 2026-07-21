"""Generates SQL fragments that resolve a fact table's coded columns against a
BD-style dicionario table (id_tabela, nome_coluna, chave, valor)."""

from pathlib import Path


class DictionaryResolver:
    """Builds the LEFT JOIN + SELECT fragments for a set of coded columns."""

    def __init__(self, dicionario_path: Path, columns: list[str]) -> None:
        self.dicionario_path = dicionario_path.as_posix()
        self.columns = columns

    def select_fragment(self) -> str:
        return ",\n    ".join(f"d_{c}.valor AS {c}_desc" for c in self.columns)

    def join_fragment(self, fact_alias: str) -> str:
        joins = (
            f"""LEFT JOIN read_parquet('{self.dicionario_path}') d_{c}
    ON d_{c}.nome_coluna = '{c}' AND d_{c}.chave = {fact_alias}.{c}"""
            for c in self.columns
        )
        return "\n".join(joins)
