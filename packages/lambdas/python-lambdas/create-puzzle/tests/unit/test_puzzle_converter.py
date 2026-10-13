import uuid
from datetime import UTC, datetime

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
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
        grid=Grid(
            cells=Cells(
                [
                    Cell(Coordinates(0, 1), black=False, id=1),
                    Cell(Coordinates(1, 1), black=True),
                    Cell(Coordinates(0, 0), black=False, letter="A"),
                    Cell(Coordinates(1, 0), black=False),
                ]
            ),
            column_width=40,
            row_height=50,
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
        "grid": {
            "numberOfRows": 2,
            "numberOfColumns": 2,
            "cells": [
                {"id": 1, "coordinates": {"x": 0, "y": 1}, "black": False, "character": None},
                {"id": None, "coordinates": {"x": 1, "y": 1}, "black": True, "character": None},
                {"id": None, "coordinates": {"x": 0, "y": 0}, "black": False, "character": "A"},
                {"id": None, "coordinates": {"x": 1, "y": 0}, "black": False, "character": None},
            ],
        },
        "createdAt": puzzle.created_at.isoformat().replace("+00:00", "Z"),
    }
