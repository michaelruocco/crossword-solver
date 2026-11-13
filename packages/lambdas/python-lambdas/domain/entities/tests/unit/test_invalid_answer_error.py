from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.invalid_answer_error import InvalidAnswerError


def test_invalid_answer_error_includes_and_exposes_the_answer_id():
    answer_id = Id.across(3)

    error = InvalidAnswerError(answer_id)

    assert str(error) == "Invalid answer for clue 3A"
    assert error.answer_id == answer_id
