from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id


def test_with_id_preserves_value_and_confidence_score():
    answer = Answer(Id.across(3), "CAT", confidence_score=87)

    updated_answer = answer.with_id(Id.down(4))

    assert updated_answer == Answer(Id.down(4), "CAT", confidence_score=87)
    assert answer.id == Id.across(3)


def test_confidence_score_defaults_to_zero():
    assert Answer(Id.across(3), "CAT").confidence_score == 0


def test_no_match_can_be_created_from_a_clue_or_id():
    clue = Clue(Id.down(4), "A clue", [3])

    assert Answer.no_match(clue) == Answer(Id.down(4), "NO_MATCH")
    assert Answer.no_match(clue.id) == Answer(Id.down(4), "NO_MATCH")


def test_answer_helpers_preserve_fields_and_return_updated_copies():
    answer = Answer(Id.across(3), "CAT", confidence_score=87)

    assert answer.with_value("DOG") == Answer(Id.across(3), "DOG", confidence_score=87)
    assert answer.numeric_id == 3
    assert answer.direction == Direction.ACROSS
    assert answer.id_as_string == "3A"
    assert answer.has_direction(Direction.ACROSS)
    assert not answer.has_direction(Direction.DOWN)
    assert answer.has_same_value(Answer(Id.down(1), "CAT"))
    assert not answer.has_same_value(Answer(Id.down(1), "cat"))
    assert answer.as_string() == "3A CAT 87"


def test_letter_at_and_matches_handle_bounds_and_unknown_pattern_characters():
    answer = Answer(Id.across(3), "CAT")

    assert answer.letter_at(0) == "C"
    assert answer.letter_at(-1) is None
    assert answer.letter_at(3) is None
    assert answer.matches("C?T")
    assert not answer.matches("D?T")
    assert not answer.matches("CATD")
    assert answer.matches("????")


def test_matches_known_digits_in_numeric_patterns():
    answer = Answer(Id.across(3), "42")

    assert answer.matches("4?")
    assert not answer.matches("3?")
