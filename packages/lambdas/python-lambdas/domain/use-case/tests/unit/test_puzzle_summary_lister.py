from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from crossword_solver_domain_use_case.puzzle_summary_lister import PuzzleSummaryLister


def test_list_all_projects_each_puzzle():
    puzzle_id = uuid4()
    created_at = datetime(2026, 10, 17, 9, 30, tzinfo=UTC)
    puzzle = SimpleNamespace(id=puzzle_id, name="puzzle14", created_at=created_at, clues=["across", "down"])
    repository = Mock()
    repository.find_all.return_value = [cast(Puzzle, puzzle)]

    summaries = PuzzleSummaryLister(repository).list_all()

    repository.find_all.assert_called_once_with()
    assert summaries == [PuzzleSummary(puzzle_id, "puzzle14", created_at, 2)]


def test_list_all_returns_an_empty_list_when_no_puzzles_exist():
    repository = Mock()
    repository.find_all.return_value = []

    assert PuzzleSummaryLister(repository).list_all() == []
    repository.find_all.assert_called_once_with()
