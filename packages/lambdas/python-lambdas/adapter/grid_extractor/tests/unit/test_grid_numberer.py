from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates

from crossword_solver_adapter_grid_extractor.grid_numberer import StructuralGridNumberer


def test_numbers_answer_starts_in_reading_order_without_changing_input_order():
    # A black centre separates the middle row and column into single-cell runs.
    cells = [Cell(Coordinates(x, y), black=(x == y == 1)) for y in range(3) for x in range(3)]

    numbered = StructuralGridNumberer().number(cells)

    assert [cell.coordinates for cell in numbered] == [cell.coordinates for cell in cells]
    assert {cell.coordinates: cell.id for cell in numbered if cell.id is not None} == {
        Coordinates(0, 2): 1,
        Coordinates(2, 2): 2,
        Coordinates(0, 0): 3,
    }
    assert all(cell.id is None for cell in cells)
    assert [cell.black for cell in numbered] == [cell.black for cell in cells]


def test_clears_previous_ids_and_preserves_letters():
    cells = [
        Cell(Coordinates(0, 0), black=False, id=99, letter="A"),
        Cell(Coordinates(1, 0), black=False, id=88),
        Cell(Coordinates(2, 0), black=True, id=77),
    ]

    numbered = StructuralGridNumberer().number(cells)

    assert [cell.id for cell in numbered] == [1, None, None]
    assert numbered[0].letter == "A"


def test_isolated_white_cell_is_not_an_answer():
    assert StructuralGridNumberer().number([Cell(Coordinates(0, 0), black=False, id=7)]) == [
        Cell(Coordinates(0, 0), black=False)
    ]


def test_empty_grid():
    assert StructuralGridNumberer().number([]) == []
