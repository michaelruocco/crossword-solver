from pathlib import Path

import cv2
import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.grid_finder import GridFinder

pytestmark = pytest.mark.integration

TESTS_DIR = Path(__file__).parent.parent
PUZZLES_DIR = TESTS_DIR / "resources" / "puzzles"
GRIDS_DIR = PUZZLES_DIR / "grids"
OUTPUT_DIR = TESTS_DIR / "output"
PUZZLES = sorted(path for path in PUZZLES_DIR.iterdir() if path.is_file())

# Allows for tiny floating point differences between OpenCV builds and platforms.
MAX_MEAN_DIFFERENCE = 1.0


@pytest.fixture
def finder() -> GridFinder:
    return GridFinder()


def mean_difference(actual: np.ndarray, expected: np.ndarray) -> float:
    if actual.shape != expected.shape:
        return float("inf")
    return float(cv2.absdiff(actual, expected).mean())


@pytest.mark.parametrize("image_path", PUZZLES, ids=lambda path: path.name)
def test_find_grid_matches_expected_image(finder, image_path):
    expected_path = GRIDS_DIR / f"{image_path.stem}.png"
    expected = cv2.imread(str(expected_path))
    assert expected is not None, f"missing expected image {expected_path}"
    image = cv2.imread(str(image_path))
    assert image is not None

    grid = finder.find_grid(image)

    difference = mean_difference(grid, expected)
    if difference > MAX_MEAN_DIFFERENCE:
        OUTPUT_DIR.mkdir(exist_ok=True)
        cv2.imwrite(str(OUTPUT_DIR / expected_path.name), grid)
    assert difference <= MAX_MEAN_DIFFERENCE, (
        f"grid differs from {expected_path.name} (shape {grid.shape} vs {expected.shape}, "
        f"mean difference {difference}), actual result written to {OUTPUT_DIR}"
    )
