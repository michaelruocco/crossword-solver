import logging

import cv2
import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates

from .mat_converter import MatConverter
from .number_detector import NumberDetector
from .rects import keep_outermost

logger = logging.getLogger(__name__)

WHITE = (255, 255, 255)


class CellFactory:
    DARK_INTENSITY = 100
    BINARY_BLOCK_SIZE = 19
    BINARY_C = 7
    # A digit's contour must cover between these percentages of the cell's area...
    MIN_DIGIT_AREA_PERCENT = 0.75
    MAX_DIGIT_AREA_PERCENT = 8
    # ...and be less than this percentage of the cell's width and height.
    MAX_DIGIT_SIZE_PERCENT = 45
    DIGIT_BORDER_FACTOR = 1.5
    # Larger scales were no more accurate on the test puzzles but made each OCR call much slower.
    DIGIT_SCALE = 10
    # Narrow digits (typically "1") are widened to this width/height ratio and retried if they can't be read.
    MIN_DIGIT_ASPECT = 0.6

    def __init__(self, detector: NumberDetector, converter: MatConverter | None = None):
        self.detector = detector
        self.converter = converter or MatConverter()

    def to_cell(self, image: np.ndarray, x: int, y: int) -> Cell:
        coordinates = Coordinates(x, y)
        if self._is_mostly_dark(image):
            return Cell(coordinates, black=True)
        return Cell(coordinates, black=False, id=self._to_id(self._find_digits(image)))

    def _is_mostly_dark(self, image: np.ndarray) -> bool:
        gray = self.converter.to_grayscale(image)
        dark_pixels = int(np.count_nonzero(gray < self.DARK_INTENSITY))
        return dark_pixels > gray.size // 2

    def _find_digits(self, image: np.ndarray) -> list[np.ndarray]:
        binary = self.converter.to_binary(
            self.converter.to_grayscale(image),
            c=self.BINARY_C,
            block_size=self.BINARY_BLOCK_SIZE,
        )
        contours = sorted(
            self.converter.to_contours(binary, cv2.RETR_LIST),
            key=lambda contour: cv2.boundingRect(contour)[0],
        )
        digits = keep_outermost([contour for contour in contours if self._is_likely_digit(binary, contour)])
        return [self._to_digit(binary, contour) for contour in digits]

    def _is_likely_digit(self, binary: np.ndarray, contour: np.ndarray) -> bool:
        x, y, width, height = cv2.boundingRect(contour)
        if x == 0 or y == 0:
            return False
        area_percent = cv2.contourArea(contour) / binary.size * 100
        if not self.MIN_DIGIT_AREA_PERCENT < area_percent < self.MAX_DIGIT_AREA_PERCENT:
            return False
        rows, columns = binary.shape
        return height / rows * 100 < self.MAX_DIGIT_SIZE_PERCENT and width / columns * 100 < self.MAX_DIGIT_SIZE_PERCENT

    def _to_digit(self, binary: np.ndarray, contour: np.ndarray) -> np.ndarray:
        x, y, width, height = cv2.boundingRect(contour)
        return self.converter.invert(binary[y : y + height, x : x + width])

    def _to_id(self, digits: list[np.ndarray]) -> int | None:
        numbers = [number for number in (self._to_number(digit) for digit in digits) if number is not None]
        if not numbers:
            return None
        return int("".join(str(number) for number in numbers))

    def _to_number(self, digit: np.ndarray) -> int | None:
        number = self.detector.detect(self.converter.scale(self._add_border(digit), self.DIGIT_SCALE))
        if number is not None:
            return number
        height, width = digit.shape[:2]
        target_width = int(height * self.MIN_DIGIT_ASPECT)
        if width >= target_width:
            return None
        logger.info("Widening digit from aspect %.2f to %.2f", width / height, self.MIN_DIGIT_ASPECT)
        widened = cv2.resize(digit, (target_width, height), interpolation=cv2.INTER_NEAREST)
        return self._to_number(widened)

    def _add_border(self, digit: np.ndarray) -> np.ndarray:
        height, width = digit.shape[:2]
        bordered = np.full(
            (int(height * self.DIGIT_BORDER_FACTOR), int(width * self.DIGIT_BORDER_FACTOR), 3),
            WHITE,
            dtype=np.uint8,
        )
        x = (bordered.shape[1] - width) // 2
        y = (bordered.shape[0] - height) // 2
        bordered[y : y + height, x : x + width] = digit
        return bordered
