from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_use_case.attempt_lister import AttemptLister


def test_lists_attempts_for_the_puzzle():
    puzzle_id = uuid4()
    puzzle = Mock(id=puzzle_id)
    attempts = [Mock()]
    puzzle_finder = Mock()
    puzzle_finder.find_by_id.return_value = puzzle
    repository = Mock()
    repository.find_by_puzzle.return_value = attempts

    result = AttemptLister(puzzle_finder, repository).list_by_puzzle_id(puzzle_id)

    assert result == attempts
    puzzle_finder.find_by_id.assert_called_once_with(puzzle_id)
    repository.find_by_puzzle.assert_called_once_with(puzzle)
