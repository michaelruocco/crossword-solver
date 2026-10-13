import re
import shutil
from pathlib import Path

import cv2
import pytest

from crossword_solver_adapter_grid_extractor.cell_factory import CellFactory

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract is not installed"),
]

CELLS_DIR = Path(__file__).parent.parent / "resources" / "puzzles" / "cells"
# File names give the number in the cell, with an optional variant, e.g. "cell-22.png" or "cell-22-b.png".
CELL_NAME = re.compile(r"cell-(\d+)(-.+)?")
CELLS = sorted(CELLS_DIR.iterdir())


@pytest.fixture
def factory(number_detector) -> CellFactory:
    return CellFactory(number_detector)


def expected_id(cell_path: Path) -> int:
    match = CELL_NAME.fullmatch(cell_path.stem)
    assert match is not None, f"cell image name {cell_path.name} does not match cell-<number>[-<variant>]"
    return int(match.group(1))


@pytest.mark.parametrize("cell_path", CELLS, ids=lambda path: path.name)
def test_reads_id_from_cell(factory, cell_path):
    image = cv2.imread(str(cell_path))
    assert image is not None

    cell = factory.to_cell(image, 0, 0)

    assert not cell.black
    assert cell.id == expected_id(cell_path)
