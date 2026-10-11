import math
from dataclasses import dataclass

import cv2
import numpy as np

Point = tuple[float, float]


@dataclass(frozen=True)
class Corners:
    top_left: Point
    top_right: Point
    bottom_right: Point
    bottom_left: Point

    def perspective_transform(self, scale: float) -> np.ndarray:
        source = np.array(self._expanded_points(scale), dtype=np.float32)
        return cv2.getPerspectiveTransform(source, self._destination_points())

    def max_size(self) -> tuple[int, int]:
        return self._max_width(), self._max_height()

    def center(self) -> Point:
        points = self._points()
        return sum(x for x, _ in points) / 4.0, sum(y for _, y in points) / 4.0

    def draw_onto(self, image: np.ndarray) -> None:
        for x, y in self._points():
            cv2.circle(image, (int(x), int(y)), 10, (0, 0, 255), 5)

    def _points(self) -> tuple[Point, Point, Point, Point]:
        return self.top_left, self.top_right, self.bottom_right, self.bottom_left

    def _expanded_points(self, scale: float) -> list[Point]:
        center_x, center_y = self.center()
        return [(center_x + (x - center_x) * scale, center_y + (y - center_y) * scale) for x, y in self._points()]

    def _destination_points(self) -> np.ndarray:
        width, height = self.max_size()
        return np.array(
            [(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)],
            dtype=np.float32,
        )

    def _max_width(self) -> int:
        return int(max(math.dist(self.bottom_right, self.bottom_left), math.dist(self.top_right, self.top_left)))

    def _max_height(self) -> int:
        return int(max(math.dist(self.top_left, self.bottom_left), math.dist(self.top_right, self.bottom_right)))
