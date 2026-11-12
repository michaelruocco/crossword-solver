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
