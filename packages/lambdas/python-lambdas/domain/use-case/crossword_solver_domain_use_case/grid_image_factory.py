from typing import Protocol

from crossword_solver_domain_entities.grid import Grid


class GridImageFactory(Protocol):
    def to_png(self, grid: Grid) -> bytes: ...
