from typing import Protocol

from crossword_solver_domain_entities.grid import Grid

from .image import Image


class GridExtractor(Protocol):
    def extract_grid(self, image: Image) -> Grid: ...
