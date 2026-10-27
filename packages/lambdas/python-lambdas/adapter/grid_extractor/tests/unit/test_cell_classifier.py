import numpy as np
import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates

from crossword_solver_adapter_grid_extractor.cell_classifier import CellClassifier


@pytest.mark.parametrize(("intensity", "black"), [(0, True), (30, True), (100, False), (255, False)])
def test_classifies_uniform_cells(intensity, black):
    image = np.full((20, 20, 3), intensity, dtype=np.uint8)

    assert CellClassifier().to_cell(image, 3, 4) == Cell(Coordinates(3, 4), black=black)


@pytest.mark.parametrize(("dark_pixels", "black"), [(200, False), (201, True)])
def test_requires_more_than_half_the_pixels_to_be_dark(dark_pixels, black):
    image = np.full((20, 20, 3), 255, dtype=np.uint8)
    image.reshape(-1, 3)[:dark_pixels] = 0

    assert CellClassifier().to_cell(image, 0, 0) == Cell(Coordinates(0, 0), black=black)
