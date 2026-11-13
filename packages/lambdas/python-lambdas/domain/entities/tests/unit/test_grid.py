import pytest

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cell_not_found_for_id_error import CellNotFoundForIdError
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id


def white_cell(x: int, y: int) -> Cell:
    return Cell(Coordinates(x, y), black=False)


def test_cells_are_iterable_and_sized():
    cells = Cells([white_cell(0, 0), white_cell(1, 0)])

    assert list(cells) == cells.values
    assert len(cells) == 2


def test_number_of_rows_and_columns_count_zero_based_coordinates():
    grid = Grid(
        cells=Cells([white_cell(x, y) for x in range(3) for y in range(2)]),
        column_width=10,
        row_height=10,
    )

    assert grid.number_of_rows == 2
    assert grid.number_of_columns == 3


def test_empty_grid_has_no_rows_or_columns():
    grid = Grid(cells=Cells([]), column_width=10, row_height=10)

    assert grid.number_of_rows == 0
    assert grid.number_of_columns == 0


def test_counts_across_cells_until_the_next_black_cell():
    grid = Grid(
        Cells(
            [
                Cell(Coordinates(0, 0), black=False, id=1),
                white_cell(1, 0),
                white_cell(2, 0),
                Cell(Coordinates(3, 0), black=True),
                white_cell(4, 0),
            ]
        ),
        10,
        10,
    )

    assert grid.count_contiguous_cells(Id.across(1)) == 3


def test_counts_down_cells_until_the_next_black_cell():
    grid = Grid(
        Cells(
            [
                Cell(Coordinates(0, 2), black=False, id=1),
                white_cell(0, 1),
                Cell(Coordinates(0, 0), black=True),
                white_cell(0, -1),
            ]
        ),
        10,
        10,
    )

    assert grid.count_contiguous_cells(Id.down(1)) == 2


def test_raises_existing_missing_cell_error_when_clue_number_is_not_on_grid():
    grid = Grid(cells=Cells([white_cell(0, 0)]), column_width=10, row_height=10)

    with pytest.raises(CellNotFoundForIdError, match="Cell not found for id 1"):
        grid.count_contiguous_cells(Id.across(1))
