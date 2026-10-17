from datetime import UTC, datetime
from uuid import uuid4

from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary
from crossword_solver_domain_entities.words import Words


def test_from_puzzle_projects_the_summary_fields():
    puzzle_id = uuid4()
    created_at = datetime(2026, 10, 17, 9, 30, tzinfo=UTC)
    puzzle = Puzzle(
        id=puzzle_id,
        name="puzzle14",
        format=".jpg",
        hash="hash-value",
        clues=Clues([Clue(Id.across(1), "Across", [4]), Clue(Id.down(2), "Down", [3])]),
        grid=Grid(Cells([]), column_width=1, row_height=1),
        words=Words([]),
        created_at=created_at,
    )

    summary = PuzzleSummary.from_puzzle(puzzle)

    assert summary == PuzzleSummary(puzzle_id, "puzzle14", created_at, 2)
