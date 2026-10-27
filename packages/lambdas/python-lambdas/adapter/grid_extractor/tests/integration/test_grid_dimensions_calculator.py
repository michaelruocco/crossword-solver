from pathlib import Path

import cv2
import pytest

from crossword_solver_adapter_grid_extractor.grid_dimensions_calculator import GridDimensionsCalculator

pytestmark = pytest.mark.integration

GRIDS_DIR = Path(__file__).parent.parent / "resources" / "puzzles" / "grids"

# Rows x columns of each puzzle's grid.
EXPECTED_DIMENSIONS = {
    "puzzle1": (13, 13),
    "puzzle2": (13, 13),
    "puzzle3": (13, 13),
    "puzzle4": (13, 13),
    "puzzle5": (13, 13),
    "puzzle9": (29, 13),
    "puzzle14": (23, 11),
    "puzzle24": (15, 15),
    "math-puzzle": (10, 10),
    "zen-puzzle": (13, 13),
}


@pytest.mark.parametrize(("puzzle", "expected"), EXPECTED_DIMENSIONS.items(), ids=EXPECTED_DIMENSIONS.keys())
def test_calculates_dimensions_of_puzzle_grid(puzzle, expected):
    grid = cv2.imread(str(GRIDS_DIR / f"{puzzle}.png"))
    assert grid is not None

    dimensions = GridDimensionsCalculator().calculate_dimensions(grid)

    assert (dimensions.number_of_rows, dimensions.number_of_columns) == expected
    assert len(dimensions.points) == expected[0] + 1
    assert all(len(row) == expected[1] + 1 for row in dimensions.points)


@pytest.mark.parametrize(("puzzle", "expected"), [("math-puzzle", 10), ("zen-puzzle", 13)])
@pytest.mark.parametrize("scale", [1.0, 1.5, 2.0])
def test_detects_small_grid_boundaries_at_multiple_resolutions(puzzle, expected, scale):
    grid = cv2.imread(str(GRIDS_DIR / f"{puzzle}.png"))
    assert grid is not None
    if scale != 1:
        grid = cv2.resize(grid, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    dimensions = GridDimensionsCalculator().calculate_dimensions(grid)

    assert dimensions.number_of_rows == dimensions.number_of_columns == expected
    assert 0 <= dimensions.rows[0] < dimensions.rows[-1] < grid.shape[0]
    assert 0 <= dimensions.columns[0] < dimensions.columns[-1] < grid.shape[1]
    assert dimensions.rows[-1] - dimensions.rows[0] > grid.shape[0] * 0.8
    assert dimensions.columns[-1] - dimensions.columns[0] > grid.shape[1] * 0.8
