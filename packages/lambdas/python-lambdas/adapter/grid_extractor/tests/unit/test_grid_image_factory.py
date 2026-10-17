import cv2
import numpy as np
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
    assert image.shape == (2 * (8 * 4 + 14), 2 * (10 * 4 + 14))
    assert image[10, 10] == 255
    assert image[10, 10 + 10 * 4 + 14] == 0


def test_to_png_rejects_a_grid_with_a_missing_coordinate():
    grid = Grid(cells=Cells([Cell(Coordinates(1, 1), black=False)]), column_width=10, row_height=8)

    try:
        GridImageFactory().to_png(grid)
    except ValueError as error:
        assert str(error) == "Grid is missing cell at (0, 1)"
    else:
        raise AssertionError("Expected ValueError for a missing cell")
