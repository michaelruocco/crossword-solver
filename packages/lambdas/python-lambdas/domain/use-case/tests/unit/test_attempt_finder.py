from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.attempt import Attempt

from crossword_solver_domain_use_case.attempt_finder import AttemptFinder
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.attempt_repository import AttemptRepository


def test_find_by_id_returns_the_attempt_from_the_repository():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    attempt = Mock(spec=Attempt)
    repository = Mock(spec=AttemptRepository)
    repository.find_by_id.return_value = attempt
    finder = AttemptFinder(repository)

    result = finder.find_by_id(puzzle_id, attempt_id)

    assert result is attempt
    repository.find_by_id.assert_called_once_with(puzzle_id, attempt_id)


def test_find_by_id_raises_with_both_ids_when_attempt_is_missing():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    repository = Mock(spec=AttemptRepository)
    repository.find_by_id.return_value = None
    finder = AttemptFinder(repository)

    with pytest.raises(AttemptNotFoundError) as error:
        finder.find_by_id(puzzle_id, attempt_id)

    assert str(error.value) == f"Attempt {attempt_id} not found for puzzle {puzzle_id}"
    assert error.value.puzzle_id == puzzle_id
    assert error.value.attempt_id == attempt_id
    repository.find_by_id.assert_called_once_with(puzzle_id, attempt_id)