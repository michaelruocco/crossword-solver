from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.invalid_answer_error import InvalidAnswerError

from crossword_solver_domain_use_case.attempt_answer_saver import AttemptAnswerSaver


def test_saves_answer_to_attempt_found_by_puzzle_and_attempt_id():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    answer = Answer(Id.across(3), "CAT")
    finder = Mock()
    repository = Mock()
    attempt = Mock()
    updated_attempt = Mock()
    finder.find_by_id.return_value = attempt
    attempt.save_answer.return_value = updated_attempt
    attempt.accepts.return_value = True

    AttemptAnswerSaver(finder, repository).save(puzzle_id, attempt_id, answer)

    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt.save_answer.assert_called_once_with(answer)
    attempt.accepts.assert_called_once_with(answer)
    repository.save.assert_called_once_with(updated_attempt)


def test_rejects_an_invalid_answer_without_saving_the_attempt():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    answer = Answer(Id.across(3), "TOO LONG")
    finder = Mock()
    repository = Mock()
    attempt = Mock()
    finder.find_by_id.return_value = attempt
    attempt.accepts.return_value = False

    with pytest.raises(InvalidAnswerError) as error:
        AttemptAnswerSaver(finder, repository).save(puzzle_id, attempt_id, answer)

    attempt.save_answer.assert_called_once_with(answer)
    repository.save.assert_not_called()
    assert error.value.answer_id == answer.id
