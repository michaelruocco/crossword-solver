import math
import statistics
from collections import defaultdict

import cv2
import numpy as np

from .corners import Point
from .grid_dimensions import GridDimensions
from .mat_converter import MatConverter


class GridDimensionsCalculator:
    # Keep threshold windows and morphology kernels small relative to the working grid.
    MIN_WORKING_SIZE = 800
    MIN_NOISE_AREA = 1500
    # Line positions closer together than this fraction of the grid size are treated as the same line.
    CLUSTER_TOLERANCE_DIVISOR = 50

    def __init__(self, converter: MatConverter | None = None):
        self.converter = converter or MatConverter()

    def calculate_dimensions(self, image: np.ndarray) -> GridDimensions:
        original_height, original_width = image.shape[:2]
        scale = max(1.0, self.MIN_WORKING_SIZE / min(original_height, original_width))
        if scale > 1:
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        gray = self.converter.to_grayscale(image)
        binary = self.converter.to_binary(self.converter.blur(gray))
        cleaned = self.converter.remove_noise_smaller_than(self.converter.smooth(binary), self.MIN_NOISE_AREA)

        rows = self._to_line_positions(self.converter.to_horizontal_grid_lines(cleaned), axis=1)
        columns = self._to_line_positions(self.converter.to_vertical_grid_lines(cleaned), axis=0)
        if rows[-1] - rows[0] < image.shape[0] / 2 or columns[-1] - columns[0] < image.shape[1] / 2:
            raise ValueError("Grid lines do not span the cropped grid image")
        intersections = self.converter.to_points(self.converter.to_intersections(cleaned))

        points = self._to_point_rows(intersections, rows, columns)
        scale_x = image.shape[1] / original_width
        scale_y = image.shape[0] / original_height
        return GridDimensions(
            rows=[round(y / scale_y) for y in rows],
            columns=[round(x / scale_x) for x in columns],
            points=[[(x / scale_x, y / scale_y) for x, y in row] for row in points],
        )

    def _to_line_positions(self, lines: np.ndarray, axis: int) -> list[int]:
        positions = sorted(cv2.boundingRect(contour)[axis] for contour in self.converter.to_contours(lines))
        if not positions:
            raise ValueError("No grid lines found")
        tolerance = min(lines.shape[:2]) // self.CLUSTER_TOLERANCE_DIVISOR
        clustered = [positions[0]]
        for position in positions[1:]:
            if abs(position - clustered[-1]) > tolerance:
                clustered.append(position)
        return clustered

    def _to_point_rows(self, points: list[Point], rows: list[int], columns: list[int]) -> list[list[Point]]:
        expected = len(rows) * len(columns)
        if len(points) < expected:
            raise ValueError(f"Found {len(points)} grid intersections but expected {expected}")
        if len(rows) < 2 or len(columns) < 2:
            raise ValueError("At least two row and column boundaries are required")
        candidates = self._find_intersection_candidates(points, rows, columns)
        offset_x, offset_y = self._intersection_offset(candidates, rows, columns)
        return [
            [
                self._select_intersection(
                    candidates[row, column], (columns[column] + offset_x, rows[row] + offset_y), row, column
                )
                for column in range(len(columns))
            ]
            for row in reversed(range(len(rows)))
        ]

    def _find_intersection_candidates(
        self, points: list[Point], rows: list[int], columns: list[int]
    ) -> dict[tuple[int, int], list[Point]]:
        candidates: dict[tuple[int, int], list[Point]] = defaultdict(list)
        for x, y in points:
            row = min(range(len(rows)), key=lambda index, y=y: abs(rows[index] - y))
            column = min(range(len(columns)), key=lambda index, x=x: abs(columns[index] - x))
            if self._near_line(x, column, columns) and self._near_line(y, row, rows):
                candidates[row, column].append((x, y))
        for row in range(len(rows)):
            for column in range(len(columns)):
                if not candidates[row, column]:
                    raise ValueError(f"Missing grid intersection at row {row}, column {column}")
        return candidates

    @staticmethod
    def _intersection_offset(
        candidates: dict[tuple[int, int], list[Point]], rows: list[int], columns: list[int]
    ) -> Point:
        # Line positions are bounding-box origins, while intersections are centroids.
        anchors = [(row, column, values[0]) for (row, column), values in candidates.items() if len(values) == 1]
        if not anchors:
            raise ValueError("No unambiguous grid intersections available for geometric matching")
        offset_x = statistics.median(point[0] - columns[column] for row, column, point in anchors)
        offset_y = statistics.median(point[1] - rows[row] for row, column, point in anchors)
        return offset_x, offset_y

    @staticmethod
    def _select_intersection(candidates: list[Point], target: Point, row: int, column: int) -> Point:
        ranked = sorted(candidates, key=lambda point: math.dist(point, target))
        if len(ranked) > 1 and math.isclose(math.dist(ranked[0], target), math.dist(ranked[1], target)):
            raise ValueError(f"Ambiguous grid intersection at row {row}, column {column}")
        return ranked[0]

    @staticmethod
    def _near_line(position: float, index: int, lines: list[int]) -> bool:
        spacing = min(
            abs(lines[neighbour] - lines[index]) for neighbour in (index - 1, index + 1) if 0 <= neighbour < len(lines)
        )
        return abs(position - lines[index]) <= spacing / 2
