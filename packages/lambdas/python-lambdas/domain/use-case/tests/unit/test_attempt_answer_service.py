from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.attempt_answer_service import AttemptAnswerService


def test_updates_answer_and_returns_reloaded_attempt():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    answer = Answer(Id.across(3), "CAT")
    finder = Mock()
    repository = Mock()
    service = AttemptAnswerService(finder, repository)
    service.saver = Mock()
    updated_attempt = Mock()
    finder.find_by_id.return_value = updated_attempt

    result = service.update_answer(puzzle_id, attempt_id, answer)

    service.saver.save.assert_called_once_with(puzzle_id, attempt_id, answer)
    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    assert result is updated_attempt


def test_deletes_answer_and_returns_reloaded_attempt():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    answer_id = Id.down(23)
    finder = Mock()
    repository = Mock()
    service = AttemptAnswerService(finder, repository)
    service.deleter = Mock()
    updated_attempt = Mock()
    finder.find_by_id.return_value = updated_attempt

    result = service.delete_answer(puzzle_id, attempt_id, answer_id)

    service.deleter.delete.assert_called_once_with(puzzle_id, attempt_id, answer_id)
    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    assert result is updated_attempt
