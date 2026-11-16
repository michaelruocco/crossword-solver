import pytest

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.id import Id


@pytest.fixture
def clue() -> Clue:
    return Clue(id=Id.across(3), text="Feline", lengths=[3])


def test_candidates_are_iterable_and_expose_clue_and_id(clue):
    answers = [Answer(clue.id, "CAT"), Answer(clue.id, "TOM")]
    candidates = Candidates(clue, answers)

    assert list(candidates) == answers
    assert len(candidates) == candidates.size() == 2
    assert candidates.clue is clue
    assert candidates.id == clue.id


def test_with_clue_reassigns_answer_ids_and_preserves_confidence(clue):
    candidates = Candidates(clue, [Answer(clue.id, "CAT", 88)])
    replacement_clue = Clue(Id.down(4), "Feline", [3])

    updated_candidates = candidates.with_clue(replacement_clue)

    assert updated_candidates.clue is replacement_clue
    assert list(updated_candidates) == [Answer(replacement_clue.id, "CAT", 88)]
    assert list(candidates) == [Answer(clue.id, "CAT", 88)]


def test_add_all_combines_candidates_by_answer_value(clue):
    candidates = Candidates(clue, [Answer(clue.id, "CAT", 80), Answer(clue.id, "TOM", 60)])
    other_candidates = Candidates(
        Clue(Id.down(4), "Feline", [3]),
        [Answer(Id.down(4), "CAT", 95), Answer(Id.down(4), "LYNX", 70)],
    )

    combined = candidates.add_all(other_candidates)

    assert list(combined) == [
        Answer(Id.down(4), "CAT", 95),
        Answer(clue.id, "TOM", 60),
        Answer(Id.down(4), "LYNX", 70),
    ]
    assert combined.clue is clue


def test_best_answer_and_score_use_highest_confidence_candidate(clue):
    candidates = Candidates(
        clue,
        [Answer(clue.id, "CAT", 70), Answer(clue.id, "TOM", 90), Answer(clue.id, "LION", 50)],
    )

    assert candidates.best() == Answer(clue.id, "TOM", 90)
    assert candidates.best_score() == 90
    assert candidates.alternative_scores() == [90, 50]
    assert candidates.values_as_string() == "CAT, TOM, LION"
    assert "has 3 candidates and best score 90" in candidates.as_string()


def test_best_answer_is_only_returned_when_overall_score_exceeds_threshold(clue):
    candidates = Candidates(clue, [Answer(clue.id, "CAT", 90)])

    assert candidates.get_best_answer_if_overall_score_greater_than(-1) == candidates.best()
    assert candidates.get_best_answer_if_overall_score_greater_than(candidates.overall_score()) is None


def test_valid_answers_match_normalized_length_and_known_pattern_letters():
    clue = Clue(Id.across(3), "A feline", [3], pattern="C?T")
    candidates = Candidates(
        clue,
        [
            Answer(clue.id, "CAT"),
            Answer(clue.id, "C O T"),
            Answer(clue.id, "BAT"),
            Answer(clue.id, "CATS"),
        ],
    )

    assert list(candidates.valid_answers(clue)) == [Answer(clue.id, "CAT")]


def test_empty_candidates_have_zero_score_and_no_best_answer(clue):
    candidates = Candidates(clue)

    assert candidates.is_empty()
    assert candidates.best() is None
    assert candidates.best_score() == 0
    assert candidates.get_best_answer_if_overall_score_greater_than(-1) is None
    assert candidates.overall_score() == 0
    assert candidates.values_as_string() == ""


def test_valid_answers_supports_a_zero_length_clue():
    clue = Clue(Id.across(1), "Empty", [])

    assert list(Candidates(clue, [Answer(clue.id, "")]).valid_answers(clue)) == [Answer(clue.id, "")]


def test_as_string_includes_pattern_and_clue_id(clue):
    assert Candidates(clue, [Answer(clue.id, "CAT", 85)]).as_string() == (
        "clue 3A Feline ??? -> has 1 candidates and best score 85 CAT"
    )


def test_with_clue_preserves_pattern_candidates_and_other_properties(clue):
    candidates = Candidates(clue, [Answer(clue.id, "CAT", 85)])
    populated_clue = clue.with_pattern("C?T").with_candidates(candidates)

    updated = populated_clue.with_id(Id.down(4)).with_text("Cat")

    assert updated.id == Id.down(4)
    assert updated.text == "Cat"
    assert updated.pattern == "C?T"
    assert updated.candidates is candidates
