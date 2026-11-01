from unittest.mock import Mock, call
from uuid import uuid4

from crossword_solver_domain_use_case.puzzle_deleter import PuzzleDeleter


def test_delete_removes_puzzle_then_attempts():
    puzzle_id = uuid4()
    repository = Mock()
    attempt_repository = Mock()
    calls = Mock()
    calls.attach_mock(attempt_repository, "attempts")
    calls.attach_mock(repository, "puzzles")
    deleter = PuzzleDeleter(repository, attempt_repository)

    deleter.delete(puzzle_id)

    attempt_repository.delete_by_puzzle_id.assert_called_once_with(puzzle_id)
    repository.delete_by_id.assert_called_once_with(puzzle_id)
    assert calls.mock_calls == [
        call.puzzles.delete_by_id(puzzle_id),
        call.attempts.delete_by_puzzle_id(puzzle_id),
    ]
