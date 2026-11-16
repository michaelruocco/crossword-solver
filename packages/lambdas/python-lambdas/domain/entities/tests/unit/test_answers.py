from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.answers import Answers
from crossword_solver_domain_entities.id import Id


def test_answers_can_be_iterated_and_found_by_clue_id():
    across_answer = Answer(Id.across(3), "CAT")
    down_answer = Answer(Id.down(1), "OWL")
    answers = Answers([across_answer, down_answer])

    assert list(answers) == [across_answer, down_answer]
    assert answers.find(Id.across(3)) == across_answer
    assert answers.find(Id.across(4)) is None


def test_deleting_an_answer_returns_a_copy_without_that_answer():
    across_answer = Answer(Id.across(3), "CAT")
    down_answer = Answer(Id.down(1), "OWL")
    answers = Answers([across_answer, down_answer])

    updated_answers = answers.delete(Id.across(3))

    assert list(answers) == [across_answer, down_answer]
    assert list(updated_answers) == [down_answer]
    assert updated_answers.find(Id.across(3)) is None


def test_deleting_a_missing_answer_is_a_no_op():
    answer = Answer(Id.across(3), "CAT")
    answers = Answers([answer])

    updated_answers = answers.delete(Id.down(1))

    assert list(updated_answers) == [answer]
