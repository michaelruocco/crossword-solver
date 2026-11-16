from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.attempt_answer_deleter import AttemptAnswerDeleter


def test_deletes_answer_from_attempt_and_saves_updated_attempt():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    answer_id = Id.down(23)
    finder = Mock()
    repository = Mock()
    attempt = Mock()
    updated_attempt = Mock()
    finder.find_by_id.return_value = attempt
    attempt.delete_answer.return_value = updated_attempt

    AttemptAnswerDeleter(finder, repository).delete(puzzle_id, attempt_id, answer_id)

    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt.delete_answer.assert_called_once_with(answer_id)
    repository.save.assert_called_once_with(updated_attempt)
