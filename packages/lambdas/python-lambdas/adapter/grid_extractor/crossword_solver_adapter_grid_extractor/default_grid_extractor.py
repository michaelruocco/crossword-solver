import logging
import time

import cv2
import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_use_case.grid_extractor import GridExtractor
from crossword_solver_domain_use_case.image import Image

from .cell_factory import CellFactory
from .grid_dimensions import GridDimensions
from .grid_dimensions_calculator import GridDimensionsCalculator
from .grid_finder import GridFinder

logger = logging.getLogger(__name__)


class DefaultGridExtractor(GridExtractor):
    def __init__(
        self,
        cell_factory: CellFactory,
        finder: GridFinder | None = None,
        calculator: GridDimensionsCalculator | None = None,
    ):
        self.cell_factory = cell_factory
        self.finder = finder or GridFinder()
        self.calculator = calculator or GridDimensionsCalculator()

    def extract_grid(self, image: Image) -> Grid:
        start = time.perf_counter()
        grid = self.finder.find_grid(_to_bgr(image))
        dimensions = self.calculator.calculate_dimensions(grid)
        cells = self._to_cells(grid, dimensions)
        duration_ms = round((time.perf_counter() - start) * 1000)
        logger.info(
            "Extracted %dx%d grid in %d ms",
            dimensions.number_of_rows,
            dimensions.number_of_columns,
            duration_ms,
            extra={"grid_extraction_duration_ms": duration_ms},
        )
        return Grid(
            cells=Cells(cells),
            column_width=dimensions.average_column_width,
            row_height=dimensions.average_row_height,
        )

    def _to_cells(self, grid: np.ndarray, dimensions: GridDimensions) -> list[Cell]:
        # y counts from the bottom row, so iterate it downwards to list cells top row first.
        return [
            self.cell_factory.to_cell(dimensions.to_cell(grid, x, y), x, y)
            for y in reversed(range(dimensions.number_of_rows))
            for x in range(dimensions.number_of_columns)
        ]


def _to_bgr(image: Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image.pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
