import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.grid_dimensions import GridDimensions

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)


@pytest.fixture
def dimensions() -> GridDimensions:
    return GridDimensions(
        rows=[0, 10, 40],
        columns=[0, 10, 30],
        points=[
            [(0.0, 40.0), (10.0, 40.0), (30.0, 40.0)],
            [(0.0, 10.0), (10.0, 10.0), (30.0, 10.0)],
            [(0.0, 0.0), (10.0, 0.0), (30.0, 0.0)],
        ],
    )


def two_by_two_grid() -> np.ndarray:
    image = np.zeros((41, 31, 3), dtype=np.uint8)
    image[0:10, 0:10] = RED
    image[0:10, 10:31] = GREEN
    image[10:41, 0:10] = BLUE
    image[10:41, 10:31] = WHITE
    return image


def test_number_of_rows_and_columns(dimensions):
    assert dimensions.number_of_rows == 2
    assert dimensions.number_of_columns == 2


def test_column_width(dimensions):
    assert dimensions.column_width(0) == 10
    assert dimensions.column_width(1) == 20


def test_row_height_counts_y_from_the_bottom(dimensions):
    assert dimensions.row_height(0) == 30
    assert dimensions.row_height(1) == 10


@pytest.mark.parametrize(
    ("columns", "expected"),
    [
        ([0, 10, 30, 45], 15),
        ([0, 10, 30], 15),
        ([0, 10, 25], 12),
    ],
    ids=["odd count uses middle width", "even count averages middle widths", "result truncated to whole pixels"],
)
def test_average_column_width_is_median(columns, expected):
    dimensions = GridDimensions(rows=[0, 10], columns=columns, points=[])

    assert dimensions.average_column_width == expected


def test_average_row_height_is_median():
    dimensions = GridDimensions(rows=[0, 20, 40, 70], columns=[0, 10], points=[])

    assert dimensions.average_row_height == 20


@pytest.mark.parametrize(
    ("x", "y", "expected_shape", "expected_colour"),
    [
        (0, 0, (30, 10, 3), BLUE),
        (1, 0, (30, 20, 3), WHITE),
        (0, 1, (10, 10, 3), RED),
        (1, 1, (10, 20, 3), GREEN),
    ],
    ids=["bottom left", "bottom right", "top left", "top right"],
)
def test_to_cell_counts_y_from_the_bottom(dimensions, x, y, expected_shape, expected_colour):
    cell = dimensions.to_cell(two_by_two_grid(), x, y)

    assert cell.shape == expected_shape
    height, width = expected_shape[:2]
    assert tuple(cell[height // 2, width // 2]) == expected_colour
