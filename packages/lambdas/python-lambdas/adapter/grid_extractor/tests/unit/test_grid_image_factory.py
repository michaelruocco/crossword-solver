import cv2
import numpy as np
import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid

from crossword_solver_adapter_grid_extractor.grid_image_factory import GridImageFactory


def test_to_png_renders_a_grid_with_black_cells_and_white_cells():
    grid = Grid(
        cells=Cells(
            [
                Cell(Coordinates(0, 0), black=False),
                Cell(Coordinates(1, 0), black=True),
                Cell(Coordinates(0, 1), black=False),
                Cell(Coordinates(1, 1), black=False, id=1, letter="A"),
            ]
        ),
        column_width=10,
        row_height=8,
    )

    encoded = GridImageFactory().to_png(grid)
    image = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

    assert image is not None
    assert encoded.startswith(b"\x89PNG\r\n\x1a\n")
    assert image.shape == (132, 132)
    assert image[80, 10] == 255
    assert image[80, 76] == 0


def test_rendering_is_independent_of_source_cell_dimensions():
    cells = Cells([Cell(Coordinates(0, 0), black=False, id=123, letter="W")])
    factory = GridImageFactory()

    assert factory.to_png(Grid(cells, column_width=10, row_height=8)) == factory.to_png(
        Grid(cells, column_width=200, row_height=150)
    )


@pytest.mark.parametrize("number", [1, 35, 123, 1234567890])
def test_id_is_confined_to_upper_label_region(number):
    grid = Grid(Cells([Cell(Coordinates(0, 0), black=False, id=number)]), column_width=1, row_height=1)

    image = cv2.imdecode(np.frombuffer(GridImageFactory().to_png(grid), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

    assert image is not None
    assert image.shape == (66, 66)
    assert np.any(image[4:19, 4:62] < 255)
    assert np.all(image[20:64, 2:64] == 255)


def test_letter_is_confined_to_answer_region_below_id():
    cells = Cells([Cell(Coordinates(0, 0), black=False, id=123, letter="W")])
    factory = GridImageFactory()
    image = cv2.imdecode(np.frombuffer(factory.to_png(Grid(cells, 1, 1)), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    id_only = cv2.imdecode(
        np.frombuffer(
            factory.to_png(Grid(Cells([Cell(Coordinates(0, 0), black=False, id=123)]), 1, 1)), dtype=np.uint8
        ),
        cv2.IMREAD_GRAYSCALE,
    )

    assert image is not None
    assert id_only is not None
    assert np.array_equal(image[:23], id_only[:23])
    assert np.any(image[23:61, 4:62] < 255)
    assert np.all(image[61:64, 2:64] == 255)


def test_to_png_rejects_text_that_cannot_fit_even_at_minimum_scale(monkeypatch):
    cell = Cell(Coordinates(0, 0), black=False, letter="W")
    grid = Grid(Cells([cell]), column_width=1, row_height=1)
    factory = GridImageFactory()
    monkeypatch.setattr(
        "crossword_solver_adapter_grid_extractor.grid_image_factory.cv2.getTextSize",
        lambda text, font, scale, thickness: ((100, 100), 10),
    )

    with pytest.raises(ValueError, match="Text does not fit in grid cell"):
        factory.to_png(grid)


def test_to_png_rejects_a_grid_with_a_missing_coordinate():
    grid = Grid(cells=Cells([Cell(Coordinates(1, 1), black=False)]), column_width=10, row_height=8)
    imageFactory = GridImageFactory()

    with pytest.raises(ValueError, match=r"Grid is missing cell at \(0, 1\)"):
        imageFactory.to_png(grid)


def test_to_png_raises_when_opencv_fails_to_encode(monkeypatch):
    grid = Grid(cells=Cells([Cell(Coordinates(0, 0), black=False)]), column_width=10, row_height=8)
    imageFactory = GridImageFactory()
    monkeypatch.setattr(
        "crossword_solver_adapter_grid_extractor.grid_image_factory.cv2.imencode",
        lambda extension, image: (False, np.array([], dtype=np.uint8)),
    )

    with pytest.raises(ValueError, match="Failed to encode puzzle image"):
        imageFactory.to_png(grid)
