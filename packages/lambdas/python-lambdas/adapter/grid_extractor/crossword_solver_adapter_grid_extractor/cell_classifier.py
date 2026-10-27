from typing import Protocol

import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates

from .mat_converter import MatConverter


class CellReader(Protocol):
    def to_cell(self, image: np.ndarray, x: int, y: int) -> Cell: ...


class CellClassifier:
    DARK_INTENSITY = 100

    def __init__(self, converter: MatConverter | None = None):
        self.converter = converter or MatConverter()

    def to_cell(self, image: np.ndarray, x: int, y: int) -> Cell:
        return Cell(Coordinates(x, y), black=self._is_mostly_dark(image))

    def _is_mostly_dark(self, image: np.ndarray) -> bool:
        gray = self.converter.to_grayscale(image)
        dark_pixels = int(np.count_nonzero(gray < self.DARK_INTENSITY))
        return dark_pixels > gray.size // 2
