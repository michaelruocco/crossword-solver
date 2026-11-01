from datetime import UTC, datetime
from uuid import uuid4

from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.words import Words

from crossword_solver_adapter_api.attempt_converter import AttemptConverter


def test_to_response_includes_attempt_state_and_full_puzzle():
    created_at = datetime(2026, 10, 31, 9, 30, tzinfo=UTC)
    puzzle = Puzzle(
        id=uuid4(),
        name="test-puzzle",
        format=".png",
        hash="hash-value",
        clues=Clues([]),
        grid=Grid(Cells([Cell(Coordinates(0, 0), black=False)]), column_width=1, row_height=1),
        words=Words([]),
        created_at=created_at,
    )
    attempt = Attempt(id=uuid4(), created_at=created_at, puzzle=puzzle)

    response = AttemptConverter().to_response(attempt).model_dump(by_alias=True, mode="json")

    assert response == {
        "id": str(attempt.id),
        "createdAt": "2026-10-31T09:30:00Z",
        "solving": False,
        "answerCount": 0,
        "puzzle": {
            "id": str(puzzle.id),
            "name": puzzle.name,
            "format": puzzle.format,
            "hash": puzzle.hash,
            "clues": [],
            "grid": {
                "numberOfRows": 1,
                "numberOfColumns": 1,
                "cells": [{"id": None, "coordinates": {"x": 0, "y": 0}, "black": False, "character": None}],
            },
            "words": [],
            "createdAt": "2026-10-31T09:30:00Z",
        },
    }
