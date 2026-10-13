from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.grid_dimensions_calculator import GridDimensionsCalculator
from crossword_solver_adapter_grid_extractor.mat_converter import MatConverter

CELLS = 5
CELL_SIZE = 60
MARGIN = 20


def drawn_grid() -> np.ndarray:
    size = CELLS * CELL_SIZE + 2 * MARGIN
    image = np.full((size, size, 3), 255, dtype=np.uint8)
    end = MARGIN + CELLS * CELL_SIZE
    for i in range(CELLS + 1):
        position = MARGIN + i * CELL_SIZE
        cv2.line(image, (MARGIN, position), (end, position), (0, 0, 0), 4)
        cv2.line(image, (position, MARGIN), (position, end), (0, 0, 0), 4)
    return image


def spying_converter() -> MagicMock:
    return MagicMock(wraps=MatConverter())


def test_calculates_rows_and_columns_from_grid_lines():
    dimensions = GridDimensionsCalculator().calculate_dimensions(drawn_grid())

    assert dimensions.number_of_rows == CELLS
    assert dimensions.number_of_columns == CELLS
    assert dimensions.rows == [17, 77, 137, 197, 257, 317]
    assert dimensions.columns == [17, 77, 137, 197, 257, 317]
    assert dimensions.average_row_height == CELL_SIZE
    assert dimensions.average_column_width == CELL_SIZE


def test_orders_points_bottom_to_top_then_left_to_right():
    dimensions = GridDimensionsCalculator().calculate_dimensions(drawn_grid())

    rounded = [[(round(x), round(y)) for x, y in row] for row in dimensions.points]
    lines = [MARGIN + i * CELL_SIZE for i in range(CELLS + 1)]
    assert rounded == [[(x, y) for x in lines] for y in reversed(lines)]


def test_merges_line_positions_within_tolerance():
    lines = np.zeros((400, 400), dtype=np.uint8)
    cv2.rectangle(lines, (10, 100), (100, 102), 255, -1)
    cv2.rectangle(lines, (150, 104), (250, 106), 255, -1)
    cv2.rectangle(lines, (10, 200), (100, 202), 255, -1)
    converter = spying_converter()
    converter.to_horizontal_grid_lines.return_value = lines

    dimensions = GridDimensionsCalculator(converter).calculate_dimensions(drawn_grid())

    assert dimensions.rows == [100, 200]


def test_raises_error_when_no_grid_lines_found():
    image = np.full((200, 200, 3), 255, dtype=np.uint8)
    for x in (50, 100, 150):
        cv2.circle(image, (x, 100), 5, (0, 0, 0), 2)
    calculator = GridDimensionsCalculator()

    with pytest.raises(ValueError, match="No grid lines found"):
        calculator.calculate_dimensions(image)


def test_raises_error_when_too_few_intersections_found():
    converter = spying_converter()
    converter.to_points.return_value = [(0.0, 0.0)]
    calculator = GridDimensionsCalculator(converter)
    image = drawn_grid()

    with pytest.raises(ValueError, match="Found 1 grid intersections but expected 36"):
        calculator.calculate_dimensions(image)
