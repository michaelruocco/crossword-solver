from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates

from crossword_solver_adapter_grid_extractor.cell_factory import CellFactory

BLACK = (0, 0, 0)
CELL_SIZE = 120


@pytest.fixture
def detector() -> MagicMock:
    detector = MagicMock()
    detector.detect.return_value = None
    return detector


@pytest.fixture
def factory(detector) -> CellFactory:
    return CellFactory(detector=detector)


def blank_cell() -> np.ndarray:
    return np.full((CELL_SIZE, CELL_SIZE, 3), 255, dtype=np.uint8)


def cell_with_digits(*boxes: tuple[int, int, int, int]) -> np.ndarray:
    image = blank_cell()
    for x, y, width, height in boxes:
        cv2.rectangle(image, (x, y), (x + width - 1, y + height - 1), BLACK, -1)
    return image


def test_mostly_dark_cell_is_black(factory, detector):
    dark = np.full((CELL_SIZE, CELL_SIZE, 3), 30, dtype=np.uint8)

    assert factory.to_cell(dark, 1, 2) == Cell(Coordinates(1, 2), black=True)
    detector.detect.assert_not_called()


def test_cell_without_digits_is_white(factory, detector):
    assert factory.to_cell(blank_cell(), 3, 4) == Cell(Coordinates(3, 4), black=False)
    detector.detect.assert_not_called()


def test_digits_are_read_left_to_right_to_form_the_id(factory, detector):
    numbers_by_scaled_width = {1500: 1, 1800: 2}
    detector.detect.side_effect = lambda image: numbers_by_scaled_width[image.shape[1]]
    image = cell_with_digits((50, 20, 24, 30), (20, 20, 20, 30))

    assert factory.to_cell(image, 0, 0) == Cell(Coordinates(0, 0), black=False, id=12)


def test_cell_is_white_when_no_digit_can_be_read(factory):
    image = cell_with_digits((20, 20, 20, 30))

    assert factory.to_cell(image, 0, 0) == Cell(Coordinates(0, 0), black=False)


def test_digit_is_centred_on_a_white_border_and_scaled(factory, detector):
    detector.detect.return_value = 5

    factory.to_cell(cell_with_digits((20, 20, 20, 30)), 0, 0)

    image = detector.detect.call_args.args[0]
    assert image.shape == (45 * 50, 30 * 50, 3)
    digit_top, digit_left = 7 * 50, 5 * 50
    assert image[digit_top - 1, digit_left - 1].tolist() == [255, 255, 255]
    assert image[digit_top, digit_left].tolist() == [0, 0, 0]


def test_narrow_digit_is_widened_and_retried_when_not_read(factory, detector):
    detector.detect.side_effect = [None, 7]

    cell = factory.to_cell(cell_with_digits((20, 20, 6, 30)), 0, 0)

    assert cell.id == 7
    widths = [call.args[0].shape[1] for call in detector.detect.call_args_list]
    assert widths == [int(6 * 1.5) * 50, int(18 * 1.5) * 50]


def test_narrow_digit_is_not_retried_more_than_once(factory, detector):
    factory.to_cell(cell_with_digits((20, 20, 6, 30)), 0, 0)

    assert detector.detect.call_count == 2


def test_wide_enough_digit_is_not_retried(factory, detector):
    factory.to_cell(cell_with_digits((20, 20, 20, 30)), 0, 0)

    assert detector.detect.call_count == 1


@pytest.mark.parametrize(
    "box",
    [(0, 20, 12, 30), (20, 0, 12, 30), (20, 20, 4, 4), (20, 20, 60, 60), (20, 20, 10, 60)],
    ids=["touches left edge", "touches top edge", "too small", "too large", "too tall"],
)
def test_shapes_that_are_unlikely_to_be_digits_are_ignored(factory, detector, box):
    factory.to_cell(cell_with_digits(box), 0, 0)

    detector.detect.assert_not_called()
