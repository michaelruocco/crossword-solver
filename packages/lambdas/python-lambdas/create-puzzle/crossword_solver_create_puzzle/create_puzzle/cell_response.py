from crossword_solver_domain_entities.cell import Cell
from pydantic import BaseModel

from .coordinates_response import CoordinatesResponse


class CellResponse(BaseModel):
    id: int | None
    coordinates: CoordinatesResponse
    black: bool
    character: str | None

    @classmethod
    def from_cell(cls, cell: Cell) -> CellResponse:
        return cls(
            id=cell.id,
            coordinates=CoordinatesResponse.from_coordinates(cell.coordinates),
            black=cell.black,
            character=cell.letter,
        )
