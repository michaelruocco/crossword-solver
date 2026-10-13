from collections.abc import Sequence

import cv2
import numpy as np

from .corners import Corners, Point
from .rects import contains


class MatConverter:
    GRID_BINARY_C = 5
    CORNER_SCALE = 1.15
    # Contours wider or taller than this are never treated as noise, whatever their area.
    NOISE_MAX_SIZE = 80

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

    def blur(self, image: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(image, (7, 7), 0)

    def smooth(self, image: np.ndarray) -> np.ndarray:
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, self._to_kernel(3, 3))

    def remove_noise_smaller_than(self, image: np.ndarray, min_area: int) -> np.ndarray:
        cleaned = image.copy()
        grid_bounds = cv2.boundingRect(self.to_largest_contour(cleaned))
        noise = [
            contour
            for contour in self.to_contours(image, cv2.RETR_LIST)
            if not contains(grid_bounds, cv2.boundingRect(contour)) or self._is_noise(contour, min_area)
        ]
        cv2.drawContours(cleaned, noise, -1, 0, -1)
        return cleaned

    def to_horizontal_grid_lines(self, image: np.ndarray) -> np.ndarray:
        width = max(20, image.shape[1] // 40)
        horizontals = cv2.erode(image, self._to_kernel(width, 1))
        connected = cv2.dilate(horizontals, self._to_kernel(350, 1))
        bridged = cv2.dilate(connected, self._to_kernel(1, 17))
        return cv2.erode(bridged, self._to_kernel(1, 17))

    def to_vertical_grid_lines(self, image: np.ndarray) -> np.ndarray:
        height = max(20, image.shape[0] // 40)
        verticals = cv2.erode(image, self._to_kernel(1, height))
        connected = cv2.dilate(verticals, self._to_kernel(1, 475))
        bridged = cv2.dilate(connected, self._to_kernel(17, 1))
        return cv2.erode(bridged, self._to_kernel(17, 1))

    def to_intersections(self, image: np.ndarray) -> np.ndarray:
        return self.intersect(self.to_horizontal_grid_lines(image), self.to_vertical_grid_lines(image))

    def intersect(self, first: np.ndarray, second: np.ndarray) -> np.ndarray:
        return cv2.bitwise_and(first, second)

    def combine(self, first: np.ndarray, second: np.ndarray) -> np.ndarray:
        return cv2.bitwise_or(first, second)

    def to_points(self, image: np.ndarray) -> list[Point]:
        points = []
        for contour in self.to_contours(image):
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                points.append((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]))
        return points

    def _is_noise(self, contour: np.ndarray, min_area: int) -> bool:
        _, _, width, height = cv2.boundingRect(contour)
        if width > self.NOISE_MAX_SIZE or height > self.NOISE_MAX_SIZE:
            return False
        return cv2.contourArea(contour) <= min_area

    def _to_kernel(self, width: int, height: int) -> np.ndarray:
        return cv2.getStructuringElement(cv2.MORPH_RECT, (width, height))

    def _to_grid_contour(self, image: np.ndarray) -> np.ndarray:
        binary = self.to_binary(self.to_grayscale(image), c=self.GRID_BINARY_C)
        return self.to_largest_contour(binary)
