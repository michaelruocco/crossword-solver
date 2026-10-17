from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from crossword_solver_domain_use_case.puzzle_summary_lister import PuzzleSummaryLister


def test_list_page_projects_each_puzzle_and_returns_next_cursor():
    puzzle_id = uuid4()
    created_at = datetime(2026, 10, 17, 9, 30, tzinfo=UTC)
    puzzle = SimpleNamespace(id=puzzle_id, name="puzzle14", created_at=created_at, clues=["across", "down"])
    repository = Mock()
    repository.find_page.return_value = ([cast(Puzzle, puzzle)], "next-page")

    page = PuzzleSummaryLister(repository).list_page(limit=10, cursor="current-page")

    repository.find_page.assert_called_once_with(10, "current-page")
    assert page.summaries == [PuzzleSummary(puzzle_id, "puzzle14", created_at, 2)]
    assert page.next_cursor == "next-page"


def test_list_page_returns_an_empty_page_when_no_puzzles_exist():
    repository = Mock()
    repository.find_page.return_value = ([], None)

    page = PuzzleSummaryLister(repository).list_page()

    assert page.summaries == []
    assert page.next_cursor is None
    repository.find_page.assert_called_once_with(20, None)


def test_list_page_rejects_a_limit_outside_the_supported_range():
    repository = Mock()

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        PuzzleSummaryLister(repository).list_page(limit=101)

    repository.find_page.assert_not_called()
