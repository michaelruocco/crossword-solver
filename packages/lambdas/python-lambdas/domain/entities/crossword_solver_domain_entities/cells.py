from dataclasses import dataclass

from .cell import Cell


@dataclass(frozen=True)
class Cells:
    values: list[Cell]
