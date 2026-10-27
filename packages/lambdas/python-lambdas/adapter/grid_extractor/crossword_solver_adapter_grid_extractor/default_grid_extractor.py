import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_use_case.grid_extractor import GridExtractor
from crossword_solver_domain_use_case.image import Image

from .cell_classifier import CellReader
from .grid_dimensions import GridDimensions
from .grid_dimensions_calculator import GridDimensionsCalculator
from .grid_finder import GridFinder
from .grid_numberer import GridNumberer

logger = logging.getLogger(__name__)


class DefaultGridExtractor(GridExtractor):
    # Tesseract runs as a subprocess, so extra workers overlap its startup and file I/O.
    WORKERS_PER_CPU = 2

    def __init__(
        self,
        cell_factory: CellReader,
        finder: GridFinder | None = None,
        calculator: GridDimensionsCalculator | None = None,
        max_workers: int | None = None,
        numberer: GridNumberer | None = None,
    ):
        self.cell_factory = cell_factory
        self.finder = finder or GridFinder()
        self.calculator = calculator or GridDimensionsCalculator()
        self.max_workers = max_workers or (os.cpu_count() or 1) * self.WORKERS_PER_CPU
        self.numberer = numberer

    def extract_grid(self, image: Image) -> Grid:
        start = time.perf_counter()
        grid = self.finder.find_grid(_to_bgr(image))
        dimensions = self.calculator.calculate_dimensions(grid)
        cells = self._to_cells(grid, dimensions)
        if self.numberer is not None:
            cells = self.numberer.number(cells)
        duration_ms = round((time.perf_counter() - start) * 1000)
        logger.info(
            "Extracted %dx%d grid in %d ms using %d workers on %s CPUs",
            dimensions.number_of_rows,
            dimensions.number_of_columns,
            duration_ms,
            self.max_workers,
            os.cpu_count(),
            extra={
                "grid_extraction_duration_ms": duration_ms,
                "grid_extraction_workers": self.max_workers,
                "cpu_count": os.cpu_count(),
            },
        )
        return Grid(
            cells=Cells(cells),
            column_width=dimensions.average_column_width,
            row_height=dimensions.average_row_height,
        )

    def _to_cells(self, grid: np.ndarray, dimensions: GridDimensions) -> list[Cell]:
        # y counts from the bottom row, so iterate it downwards to list cells top row first.
        positions = [
            (x, y) for y in reversed(range(dimensions.number_of_rows)) for x in range(dimensions.number_of_columns)
        ]
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(
                executor.map(
                    lambda position: self.cell_factory.to_cell(dimensions.to_cell(grid, *position), *position),
                    positions,
                )
            )


def _to_bgr(image: Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image.pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
