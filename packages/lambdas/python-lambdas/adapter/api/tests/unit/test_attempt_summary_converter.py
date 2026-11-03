from datetime import UTC, datetime
from uuid import uuid4

from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.words import Words

from crossword_solver_adapter_api.attempt_summary_converter import AttemptSummaryConverter


def test_to_response_includes_summary_fields_and_clue_count():
    created_at = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
    puzzle = Puzzle(
        id=uuid4(),
        name="test-puzzle",
        format=".png",
        hash="hash-value",
        clues=Clues(
            [
                Clue(Id.across(1), "First clue", [2]),
                Clue(Id.down(2), "Second clue", [2]),
            ]
        ),
        grid=Grid(Cells([Cell(Coordinates(0, 0), black=False)]), column_width=1, row_height=1),
        words=Words([]),
        created_at=created_at,
    )
    attempt = Attempt(
        id=uuid4(),
        created_at=created_at,
        solving=True,
        answer_count=3,
        puzzle=puzzle,
    )

    response = AttemptSummaryConverter().to_response(attempt)

    assert response.model_dump(by_alias=True, mode="json") == {
        "id": str(attempt.id),
        "createdAt": "2026-11-01T12:00:00Z",
        "solving": True,
        "answerCount": 3,
        "clueCount": 2,
    }
