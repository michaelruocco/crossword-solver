from collections.abc import Sequence

import cv2
import numpy as np

from .corners import Corners, Point


class MatConverter:
    GRID_BINARY_C = 5
    CORNER_SCALE = 1.15

    def warp_grid(self, image: np.ndarray) -> np.ndarray:
        contour = self._to_grid_contour(image)
        corners = self.order_corners(self.to_polygon_points(contour))
        transform = corners.perspective_transform(self.CORNER_SCALE)
        return cv2.warpPerspective(image, transform, corners.max_size())

    def crop(self, image: np.ndarray, expand_pixels: int) -> np.ndarray:
        x, y, width, height = cv2.boundingRect(self._to_grid_contour(image))
        new_x = max(x - expand_pixels, 0)
        new_y = max(y - expand_pixels, 0)
        new_width = min(width + 2 * expand_pixels, image.shape[1] - new_x)
        new_height = min(height + 2 * expand_pixels, image.shape[0] - new_y)
        return image[new_y : new_y + new_height, new_x : new_x + new_width]

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def to_binary(self, image: np.ndarray, c: int = 10, block_size: int = 51) -> np.ndarray:
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            c,
        )

    def to_contours(self, image: np.ndarray, mode: int = cv2.RETR_EXTERNAL) -> list[np.ndarray]:
        contours, _ = cv2.findContours(image, mode, cv2.CHAIN_APPROX_SIMPLE)
        return list(contours)

    def to_largest_contour(self, image: np.ndarray) -> np.ndarray:
        contours = self.to_contours(image)
        if not contours:
            raise ValueError("No contours found")
        return max(contours, key=cv2.contourArea)

    def to_polygon_points(self, contour: np.ndarray) -> list[Point]:
        perimeter = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        return [(float(x), float(y)) for x, y in approximation.reshape(-1, 2)]

    def order_corners(self, points: Sequence[Point]) -> Corners:
        return Corners(
            top_left=min(points, key=lambda p: p[0] + p[1]),
            top_right=min(points, key=lambda p: p[1] - p[0]),
            bottom_right=max(points, key=lambda p: p[0] + p[1]),
            bottom_left=max(points, key=lambda p: p[1] - p[0]),
        )

    def _to_grid_contour(self, image: np.ndarray) -> np.ndarray:
        binary = self.to_binary(self.to_grayscale(image), c=self.GRID_BINARY_C)
        return self.to_largest_contour(binary)
