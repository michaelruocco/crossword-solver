import logging
from unittest.mock import MagicMock

import numpy as np
import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_use_case.image import Image
from PIL import Image as PILImage

from crossword_solver_adapter_grid_extractor.default_grid_extractor import DefaultGridExtractor

FOUND_GRID = np.zeros((10, 10, 3), dtype=np.uint8)


def to_image(pil_image: PILImage.Image) -> Image:
    return Image(name="puzzle", format=".png", pil_image=pil_image, bytes=b"", hash="hash")


@pytest.fixture
def finder() -> MagicMock:
    finder = MagicMock()
    finder.find_grid.return_value = FOUND_GRID
    return finder


@pytest.fixture
def dimensions() -> MagicMock:
    dimensions = MagicMock(number_of_rows=2, number_of_columns=3, average_column_width=40, average_row_height=50)
    dimensions.to_cell.side_effect = lambda grid, x, y: f"cell image {x},{y}"
    return dimensions


@pytest.fixture
def calculator(dimensions) -> MagicMock:
    calculator = MagicMock()
    calculator.calculate_dimensions.return_value = dimensions
    return calculator


@pytest.fixture
def cell_factory() -> MagicMock:
    cell_factory = MagicMock()
    cell_factory.to_cell.side_effect = lambda image, x, y: Cell(Coordinates(x, y), black=False)
    return cell_factory


@pytest.fixture
def extractor(cell_factory, finder, calculator) -> DefaultGridExtractor:
    return DefaultGridExtractor(cell_factory, finder, calculator)


def test_lists_cells_top_row_first_left_to_right(extractor):
    grid = extractor.extract_grid(to_image(PILImage.new("RGB", (4, 4))))

    assert [cell.coordinates for cell in grid.cells.values] == [
        Coordinates(0, 1),
        Coordinates(1, 1),
        Coordinates(2, 1),
        Coordinates(0, 0),
        Coordinates(1, 0),
        Coordinates(2, 0),
    ]


def test_uses_average_cell_size(extractor):
    grid = extractor.extract_grid(to_image(PILImage.new("RGB", (4, 4))))

    assert grid.column_width == 40
    assert grid.row_height == 50


def test_builds_each_cell_from_its_image_in_the_found_grid(extractor, calculator, dimensions, cell_factory):
    extractor.extract_grid(to_image(PILImage.new("RGB", (4, 4))))

    calculator.calculate_dimensions.assert_called_once_with(FOUND_GRID)
    dimensions.to_cell.assert_any_call(FOUND_GRID, 2, 1)
    cell_factory.to_cell.assert_any_call("cell image 2,1", 2, 1)


def test_defaults_workers_to_twice_cpu_count(cell_factory, finder, calculator, monkeypatch):
    monkeypatch.setattr("os.cpu_count", lambda: 3)

    extractor = DefaultGridExtractor(cell_factory, finder, calculator)

    assert extractor.max_workers == 6


@pytest.mark.parametrize(
    ("pil_image", "expected_pixel"),
    [
        (PILImage.new("RGB", (4, 4), (255, 0, 0)), [0, 0, 255]),
        (PILImage.new("RGBA", (4, 4), (255, 0, 0, 255)), [0, 0, 255]),
        (PILImage.new("L", (4, 4), 128), [128, 128, 128]),
    ],
    ids=["rgb", "rgba", "grayscale"],
)
def test_passes_image_to_finder_as_bgr(extractor, finder, pil_image, expected_pixel):
    extractor.extract_grid(to_image(pil_image))

    image = finder.find_grid.call_args.args[0]
    assert image.shape == (4, 4, 3)
    assert image[0, 0].tolist() == expected_pixel


def test_logs_grid_size_and_extraction_duration(extractor, caplog):
    with caplog.at_level(logging.INFO):
        extractor.extract_grid(to_image(PILImage.new("RGB", (4, 4))))

    record = next(record for record in caplog.records if record.message.startswith("Extracted"))
    assert record.message.startswith("Extracted 2x3 grid in ")
    assert record.grid_extraction_duration_ms >= 0
