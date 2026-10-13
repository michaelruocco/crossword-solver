import statistics
from dataclasses import dataclass

import cv2
import numpy as np

from .corners import Point


@dataclass(frozen=True)
class GridDimensions:
    rows: list[int]
    columns: list[int]
    # Rows of intersection points ordered bottom to top, each ordered left to right.
    points: list[list[Point]]

    @property
    def number_of_rows(self) -> int:
        return len(self.rows) - 1

    @property
    def number_of_columns(self) -> int:
        return len(self.columns) - 1

    @property
    def average_column_width(self) -> int:
        return int(statistics.median(self.column_width(x) for x in range(self.number_of_columns)))

    @property
    def average_row_height(self) -> int:
        return int(statistics.median(self.row_height(y) for y in range(self.number_of_rows)))

    def column_width(self, x: int) -> int:
        return self.columns[x + 1] - self.columns[x]

    def row_height(self, y: int) -> int:
        # Top-down unlike to_cell's y, it reads all test puzzles' ids, bottom-up doesn't.
        return self.rows[y + 1] - self.rows[y]

    def to_cell(self, grid: np.ndarray, x: int, y: int) -> np.ndarray:
        width = self.column_width(x)
        height = self.row_height(y)
        source = np.array(self._source_points(x, y), dtype=np.float32)
        destination = np.array(
            [(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)],
            dtype=np.float32,
        )
        transform = cv2.getPerspectiveTransform(source, destination)
        return cv2.warpPerspective(
            grid,
            transform,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )

    def _source_points(self, x: int, y: int) -> list[Point]:
        bottom_left = self.points[y][x]
        bottom_right = self.points[y][x + 1]
        top_right = self.points[y + 1][x + 1]
        top_left = self.points[y + 1][x]
        return [top_left, top_right, bottom_right, bottom_left]
