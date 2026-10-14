from crossword_solver_domain_entities.grid import Grid
from pydantic import BaseModel, Field

from .cell_response import CellResponse


class GridResponse(BaseModel):
    number_of_rows: int = Field(alias="numberOfRows")
    number_of_columns: int = Field(alias="numberOfColumns")
    cells: list[CellResponse]

    @classmethod
    def from_grid(cls, grid: Grid) -> GridResponse:
        return cls(
            numberOfRows=grid.number_of_rows,
            numberOfColumns=grid.number_of_columns,
            cells=[CellResponse.from_cell(cell) for cell in grid.cells],
        )
