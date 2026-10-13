from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid


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
