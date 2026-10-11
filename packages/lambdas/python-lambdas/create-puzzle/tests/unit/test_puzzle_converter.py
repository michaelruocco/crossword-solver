import uuid
from datetime import UTC, datetime

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle

from crossword_solver_create_puzzle.create_puzzle.puzzle_converter import (
    PuzzleConverter,
)


def test_to_response():
    puzzle = Puzzle(
        id=uuid.uuid4(),
        name="puzzle14",
        format=".jpg",
        hash="hash-value",
        clues=Clues(
            [
                Clue(id=Id.across(1), text="Pacific republic (4)", lengths=[4]),
                Clue(id=Id.down(2), text="Muscular twitch (4)", lengths=[4]),
            ]
        ),
        created_at=datetime.now(UTC),
    )

    response = PuzzleConverter().to_response(puzzle)

    assert response.model_dump(by_alias=True, mode="json") == {
        "id": str(puzzle.id),
        "name": puzzle.name,
        "format": puzzle.format,
        "hash": puzzle.hash,
        "clues": [
            {"id": 1, "direction": "ACROSS", "text": "Pacific republic (4)", "lengths": [4]},
            {"id": 2, "direction": "DOWN", "text": "Muscular twitch (4)", "lengths": [4]},
        ],
        "createdAt": puzzle.created_at.isoformat().replace("+00:00", "Z"),
    }
