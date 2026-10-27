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
        bottom_to_top = sorted(points, key=lambda point: point[1], reverse=True)
        return [
            sorted(bottom_to_top[start : start + len(columns)], key=lambda point: point[0])
            for start in range(0, len(rows) * len(columns), len(columns))
        ]
