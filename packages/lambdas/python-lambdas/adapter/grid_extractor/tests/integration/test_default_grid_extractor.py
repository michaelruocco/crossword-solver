import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_use_case.image import Image
from PIL import Image as PILImage

from crossword_solver_adapter_grid_extractor.cell_factory import CellFactory
from crossword_solver_adapter_grid_extractor.default_grid_extractor import DefaultGridExtractor
from crossword_solver_adapter_grid_extractor.number_detector import NumberDetector

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract is not installed"),
]

PUZZLES_DIR = Path(__file__).parent.parent / "resources" / "puzzles"

# Rows x columns of each puzzle's grid.
EXPECTED_SIZES = {
    "puzzle1.png": (13, 13),
    "puzzle2.png": (13, 13),
    "puzzle3.png": (13, 13),
    "puzzle4.png": (13, 13),
    "puzzle5.png": (13, 13),
    "puzzle9.jpg": (29, 13),
    "puzzle14.jpg": (23, 11),
    "puzzle24.jpg": (15, 15),
    "web-puzzle.jpg": (15, 15)
}


@pytest.fixture(scope="module")
def extract_cells(tessdata_dir) -> Callable[[str], list[Cell]]:
    # Extraction takes around 10 seconds per puzzle, so each puzzle is only extracted once.
    extractor = DefaultGridExtractor(CellFactory(NumberDetector(tessdata_dir)))
    extracted: dict[str, list[Cell]] = {}

    def extract(name: str) -> list[Cell]:
        if name not in extracted:
            extracted[name] = extractor.extract_grid(load(name)).cells.values
        return extracted[name]

    return extract


def load(name: str) -> Image:
    pil_image = PILImage.open(PUZZLES_DIR / name)
    pil_image.load()
    return Image(name=name, format=Path(name).suffix, pil_image=pil_image, bytes=b"", hash="")


@pytest.mark.parametrize(("name", "expected"), EXPECTED_SIZES.items(), ids=EXPECTED_SIZES.keys())
def test_extracts_every_cell_of_the_grid(extract_cells, name, expected):
    rows, columns = expected

    cells = extract_cells(name)

    assert {(cell.coordinates.x, cell.coordinates.y) for cell in cells} == {
        (x, y) for x in range(columns) for y in range(rows)
    }


@pytest.mark.parametrize("name", EXPECTED_SIZES.keys())
def test_reads_ids_in_order_from_top_left(extract_cells, name):
    cells = extract_cells(name)

    ids = [cell.id for cell in cells if cell.id is not None]
    assert ids == list(range(1, len(ids) + 1))


@pytest.mark.parametrize("name", EXPECTED_SIZES.keys())
def test_extracts_expected_cells(extract_cells, name):
    expected_json = json.loads((PUZZLES_DIR / "expected_cells" / Path(name).with_suffix(".json")).read_text())
    expected = [
        Cell(coordinates=Coordinates(**cell["coordinates"]), black=cell["black"], id=cell.get("id"))
        for cell in expected_json
    ]

    cells = extract_cells(name)

    assert len(cells) == len(expected)
    assert {cell.coordinates: cell for cell in cells} == {cell.coordinates: cell for cell in expected}
