from pathlib import Path

import pytest

from crossword_solver_adapter_grid_extractor.number_detector import NumberDetector


def _find_tessdata_dir() -> Path:
    for parent in Path(__file__).parents:
        candidate = parent / "infrastructure" / "tesseract" / "tessdata"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("infrastructure/tesseract/tessdata not found above the tests directory")


@pytest.fixture(scope="session")
def tessdata_dir() -> Path:
    # Same trained model as the Lambda layer; local installs often ship the less accurate "fast" model.
    return _find_tessdata_dir()


@pytest.fixture
def number_detector(tessdata_dir) -> NumberDetector:
    return NumberDetector(tessdata_dir)
