from collections.abc import Iterator
from dataclasses import dataclass

from .cell import Cell
from .cell_not_found_for_id_error import CellNotFoundForIdError
from .coordinates import Coordinates


@dataclass(frozen=True)
class Cells:
    values: list[Cell]

    def __iter__(self) -> Iterator[Cell]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def find_coordinates_by_id(self, cell_id: int) -> Coordinates | None:
        return next((cell.coordinates for cell in self.values if cell.id == cell_id), None)

    def force_find_coordinates_by_id(self, cell_id: int) -> Coordinates:
        coordinates = self.find_coordinates_by_id(cell_id)
        if coordinates is None:
            raise CellNotFoundForIdError(cell_id)
        return coordinates
