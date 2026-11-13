import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cell_not_found_for_id_error import CellNotFoundForIdError
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.clue_length_population_policy import ClueLengthPopulationPolicy


@pytest.fixture
def grid() -> Grid:
    return Grid(
        cells=Cells(
            [
                Cell(Coordinates(0, 2), black=False, id=1),
                Cell(Coordinates(1, 2), black=False),
                Cell(Coordinates(2, 2), black=False),
                Cell(Coordinates(3, 2), black=True),
                Cell(Coordinates(4, 2), black=False, id=2),
                Cell(Coordinates(4, 1), black=False),
                Cell(Coordinates(4, 0), black=True),
            ]
        ),
        column_width=10,
        row_height=10,
    )


def test_populates_missing_lengths_in_both_directions_and_preserves_clue_data(grid: Grid):
    across = Clue(Id.across(1), "Across clue", [], ClueType.CRYPTIC)
    down = Clue(Id.down(2), "Down clue", [])

    updated = ClueLengthPopulationPolicy().populate(Clues([across, down]), grid)

    assert list(updated) == [
        Clue(Id.across(1), "Across clue", [3], ClueType.CRYPTIC),
        Clue(Id.down(2), "Down clue", [2]),
    ]


def test_returns_a_new_clues_collection_and_leaves_existing_lengths_unchanged(grid: Grid):
    clue = Clue(Id.across(1), "Across clue", [1, 2])
    clues = Clues([clue])

    updated = ClueLengthPopulationPolicy().populate(clues, grid)

    assert updated is not clues
    assert next(iter(updated)) is clue
    assert next(iter(updated)).lengths == [1, 2]


def test_stops_length_at_a_missing_grid_coordinate():
    grid = Grid(
        Cells(
            [
                Cell(Coordinates(0, 0), black=False, id=1),
                Cell(Coordinates(1, 0), black=False),
                Cell(Coordinates(3, 0), black=False),
            ]
        ),
        column_width=10,
        row_height=10,
    )
    clues = Clues([Clue(Id.across(1), "Across clue", [])])

    updated = ClueLengthPopulationPolicy().populate(clues, grid)

    assert next(iter(updated)).lengths == [2]


def test_raises_existing_missing_cell_error_for_a_clue_without_a_numbered_start(grid: Grid):
    clues = Clues([Clue(Id.across(9), "Missing clue", [])])

    with pytest.raises(CellNotFoundForIdError, match="Cell not found for id 9"):
        ClueLengthPopulationPolicy().populate(clues, grid)
