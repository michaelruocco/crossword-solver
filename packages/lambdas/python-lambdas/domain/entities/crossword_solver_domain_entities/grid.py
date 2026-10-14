from dataclasses import dataclass

from .cells import Cells


@dataclass(frozen=True)
class Grid:
    cells: Cells
    column_width: int
    row_height: int

    @property
    def number_of_rows(self) -> int:
        return max((cell.coordinates.y for cell in self.cells), default=-1) + 1

    @property
    def number_of_columns(self) -> int:
        return max((cell.coordinates.x for cell in self.cells), default=-1) + 1
