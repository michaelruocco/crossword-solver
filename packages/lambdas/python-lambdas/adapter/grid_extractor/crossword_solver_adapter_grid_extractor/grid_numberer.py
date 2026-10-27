from dataclasses import replace
from typing import Protocol

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates


class GridNumberer(Protocol):
    def number(self, cells: list[Cell]) -> list[Cell]: ...


class StructuralGridNumberer:
    """Conventional blocked-grid numbering, with answers at least two cells long."""

    def number(self, cells: list[Cell]) -> list[Cell]:
        white = {cell.coordinates for cell in cells if not cell.black}
        ids: dict[Coordinates, int] = {}
        for position in sorted(white, key=lambda p: (-p.y, p.x)):
            x, y = position.x, position.y
            across = Coordinates(x - 1, y) not in white and Coordinates(x + 1, y) in white
            down = Coordinates(x, y + 1) not in white and Coordinates(x, y - 1) in white
            if across or down:
                ids[position] = len(ids) + 1
        return [replace(cell, id=ids.get(cell.coordinates)) for cell in cells]
