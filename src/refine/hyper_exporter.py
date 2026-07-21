"""Exports refined DataFrames into a single Tableau .hyper file."""

from pathlib import Path

import pandas as pd
import pantab


class HyperExporter:
    """Writes a set of named DataFrames as tables into one .hyper file."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def export(self, tables: dict[str, pd.DataFrame]) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        pantab.frames_to_hyper(tables, self.output_path, table_mode="w")
        return self.output_path
