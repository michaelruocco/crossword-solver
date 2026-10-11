from dataclasses import dataclass

from .cells import Cells


@dataclass(frozen=True)
class Grid:
    cells: Cells
    column_width: int
    row_height: int
