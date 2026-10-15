import pytest

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cell_not_found_for_id_error import CellNotFoundForIdError
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.coordinates import Coordinates


@pytest.fixture
def cells() -> Cells:
    return Cells(
        [
            Cell(Coordinates(0, 1), black=False, id=1),
            Cell(Coordinates(1, 1), black=True),
            Cell(Coordinates(0, 0), black=False, id=2),
        ]
    )


def test_find_coordinates_by_id_returns_coordinates_of_cell_with_id(cells):
    assert cells.find_coordinates_by_id(2) == Coordinates(0, 0)


def test_find_coordinates_by_id_returns_none_when_no_cell_has_id(cells):
    assert cells.find_coordinates_by_id(9) is None


def test_force_find_coordinates_by_id_returns_coordinates_of_cell_with_id(cells):
    assert cells.force_find_coordinates_by_id(1) == Coordinates(0, 1)


def test_force_find_coordinates_by_id_raises_error_when_no_cell_has_id(cells):
    with pytest.raises(CellNotFoundForIdError, match="Cell not found for id 9") as error:
        cells.force_find_coordinates_by_id(9)

    assert error.value.cell_id == 9
