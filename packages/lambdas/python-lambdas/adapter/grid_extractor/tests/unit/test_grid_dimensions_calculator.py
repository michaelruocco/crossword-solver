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
    assert dimensions.rows == [18, 78, 138, 198, 258, 318]
    assert dimensions.columns == [18, 78, 138, 198, 258, 318]
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
    assert GridDimensionsCalculator()._to_line_positions(lines, axis=1) == [100, 200]


def test_raises_error_when_no_grid_lines_found():
    image = np.full((200, 200, 3), 255, dtype=np.uint8)
    for x in (50, 100, 150):
        cv2.circle(image, (x, 100), 5, (0, 0, 0), 2)
    calculator = GridDimensionsCalculator()

    with pytest.raises(ValueError, match="Grid lines do not span the cropped grid image"):
        calculator.calculate_dimensions(image)


def test_raises_error_when_line_mask_is_empty():
    with pytest.raises(ValueError, match="No grid lines found"):
        GridDimensionsCalculator()._to_line_positions(np.zeros((200, 200), dtype=np.uint8), axis=1)


def test_enlarges_small_grids_for_processing_and_returns_original_coordinates():
    converter = spying_converter()
    image = cv2.resize(drawn_grid(), (511, 340))

    dimensions = GridDimensionsCalculator(converter).calculate_dimensions(image)

    working_image = converter.to_grayscale.call_args.args[0]
    assert working_image.shape == (800, 1202, 3)
    assert dimensions.number_of_rows == dimensions.number_of_columns == CELLS
    expected_x = [(MARGIN + i * CELL_SIZE) * 511 / 340 for i in range(CELLS + 1)]
    expected_y = [MARGIN + i * CELL_SIZE for i in reversed(range(CELLS + 1))]
    for row, y in zip(dimensions.points, expected_y, strict=True):
        assert [point[0] for point in row] == pytest.approx(expected_x, abs=1)
        assert [point[1] for point in row] == pytest.approx([y] * (CELLS + 1), abs=1)


def test_leaves_large_grid_resolution_unchanged():
    converter = spying_converter()
    image = cv2.resize(drawn_grid(), (1020, 1020))

    GridDimensionsCalculator(converter).calculate_dimensions(image)

    assert converter.to_grayscale.call_args.args[0] is image


def test_raises_error_when_too_few_intersections_found():
    converter = spying_converter()
    converter.to_points.return_value = [(0.0, 0.0)]
    calculator = GridDimensionsCalculator(converter)
    image = drawn_grid()

    with pytest.raises(ValueError, match="Found 1 grid intersections but expected 36"):
        calculator.calculate_dimensions(image)


def test_matches_intersections_geometrically_regardless_of_input_order():
    points = [(10.0, 10.0), (110.0, 40.0), (10.0, 130.0), (110.0, 110.0)]

    result = GridDimensionsCalculator()._to_point_rows(list(reversed(points)), [0, 100], [0, 100])

    assert result == [[(10.0, 130.0), (110.0, 110.0)], [(10.0, 10.0), (110.0, 40.0)]]


def test_extra_candidates_do_not_shift_other_rows():
    points = [(10.0, 10.0), (110.0, 10.0), (10.0, 110.0), (110.0, 110.0)]
    points.extend([(80.0, 110.0), (300.0, 300.0)])

    result = GridDimensionsCalculator()._to_point_rows(points, [0, 100], [0, 100])

    assert result == [[(10.0, 110.0), (110.0, 110.0)], [(10.0, 10.0), (110.0, 10.0)]]


def test_missing_intersection_is_not_hidden_by_surplus_candidates():
    points = [(10.0, 10.0), (110.0, 10.0), (10.0, 110.0), (20.0, 110.0)]

    with pytest.raises(ValueError, match="Missing grid intersection at row 1, column 1"):
        GridDimensionsCalculator()._to_point_rows(points, [0, 100], [0, 100])


def test_distant_candidate_cannot_stand_in_for_missing_intersection():
    points = [(10.0, 10.0), (110.0, 10.0), (10.0, 110.0), (300.0, 300.0)]

    with pytest.raises(ValueError, match="Missing grid intersection at row 1, column 1"):
        GridDimensionsCalculator()._to_point_rows(points, [0, 100], [0, 100])


def test_equally_plausible_candidates_are_reported_as_ambiguous():
    points = [(10.0, 10.0), (110.0, 10.0), (10.0, 110.0), (105.0, 110.0), (115.0, 110.0)]

    with pytest.raises(ValueError, match="Ambiguous grid intersection at row 1, column 1"):
        GridDimensionsCalculator()._to_point_rows(points, [0, 100], [0, 100])


def test_requires_some_unambiguous_intersections_to_resolve_duplicates():
    points = [(x + dx, y + 10.0) for y in (0, 100) for x in (0, 100) for dx in (5.0, 15.0)]

    with pytest.raises(ValueError, match="No unambiguous grid intersections"):
        GridDimensionsCalculator()._to_point_rows(points, [0, 100], [0, 100])
