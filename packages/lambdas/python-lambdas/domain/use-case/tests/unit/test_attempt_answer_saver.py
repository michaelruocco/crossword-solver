from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.id import Id

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

    AttemptAnswerSaver(finder, repository).save(puzzle_id, attempt_id, answer)

    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt.save_answer.assert_called_once_with(answer)
    repository.save.assert_called_once_with(updated_attempt)
