from collections.abc import Iterator
from dataclasses import dataclass

from .cell import Cell


@dataclass(frozen=True)
class Cells:
    values: list[Cell]

    def __iter__(self) -> Iterator[Cell]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)
