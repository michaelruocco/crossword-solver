from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle import Puzzle

from crossword_solver_domain_use_case.attempt_creator import AttemptCreator
from crossword_solver_domain_use_case.puzzle_finder import PuzzleFinder
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError

NOW = datetime(2026, 10, 31, 9, 30, tzinfo=UTC)


def test_create_saves_an_empty_attempt_referencing_the_found_puzzle():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    puzzle = Mock(spec=Puzzle)
    puzzle.id = puzzle_id
    puzzle_repository = Mock()
    puzzle_repository.find_by_id.return_value = puzzle
    attempt_repository = Mock()
    creator = AttemptCreator(
        PuzzleFinder(puzzle_repository),
        attempt_repository,
        id_supplier=lambda: attempt_id,
        clock=lambda: NOW,
    )

    result = creator.create(puzzle_id)

    puzzle_repository.find_by_id.assert_called_once_with(puzzle_id)
    attempt_repository.save.assert_called_once()
    attempt = attempt_repository.save.call_args.args[0]
    assert attempt.id == attempt_id
    assert attempt.created_at == NOW
    assert attempt.puzzle is puzzle
    assert attempt.puzzle_id == puzzle_id
    assert attempt.solving is False
    assert attempt.answer_count == 0
    assert result == attempt_id


def test_create_propagates_missing_puzzle_without_saving_attempt():
    puzzle_id = uuid4()
    puzzle_repository = Mock()
    puzzle_repository.find_by_id.return_value = None
    attempt_repository = Mock()
    creator = AttemptCreator(PuzzleFinder(puzzle_repository), attempt_repository)

    with pytest.raises(PuzzleNotFoundError):
        creator.create(puzzle_id)

    attempt_repository.save.assert_not_called()
