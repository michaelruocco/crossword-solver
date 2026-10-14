from unittest.mock import Mock
from uuid import uuid4

import pytest

from crossword_solver_domain_use_case.puzzle_finder import PuzzleFinder
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError


def test_find_by_id_returns_puzzle_from_repository():
    puzzle_id = uuid4()
    puzzle = Mock()
    repository = Mock()
    repository.find_by_id.return_value = puzzle
    finder = PuzzleFinder(repository)

    assert finder.find_by_id(puzzle_id) is puzzle
    repository.find_by_id.assert_called_once_with(puzzle_id)


def test_find_by_id_raises_error_when_puzzle_not_found():
    puzzle_id = uuid4()
    repository = Mock()
    repository.find_by_id.return_value = None
    finder = PuzzleFinder(repository)

    with pytest.raises(PuzzleNotFoundError, match=f"Puzzle not found with id {puzzle_id}") as error:
        finder.find_by_id(puzzle_id)

    assert error.value.puzzle_id == puzzle_id
