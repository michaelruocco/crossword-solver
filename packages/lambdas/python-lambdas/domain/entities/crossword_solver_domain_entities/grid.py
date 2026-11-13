from dataclasses import dataclass

from .cells import Cells
from .coordinates import Coordinates
from .direction import Direction
from .id import Id


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

    def count_contiguous_cells(self, clue_id: Id) -> int:
        coordinates = self.cells.force_find_coordinates_by_id(clue_id.number)
        cells_by_coordinates = {cell.coordinates: cell for cell in self.cells}
        x_offset = 1 if clue_id.direction == Direction.ACROSS else 0
        y_offset = -1 if clue_id.direction == Direction.DOWN else 0
        length = 0
        while (cell := cells_by_coordinates.get(coordinates)) is not None and not cell.black:
            length += 1
            coordinates = Coordinates(coordinates.x + x_offset, coordinates.y + y_offset)
        return length
