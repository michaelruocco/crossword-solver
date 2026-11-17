import pytest
from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.id import Id

from crossword_solver_adapter_answer_finder.find_answer_response_converter import FindAnswerResponseConverter


@pytest.fixture
def converter():
    return FindAnswerResponseConverter()


def test_parses_normalizes_sorts_and_deduplicates_candidates(converter):
    candidates = converter.to_candidates(
        "Candidates:\n1A|c a t|75\nmalformed line\n1A|DOG|90\n1A|CAT|95\n1A|DOG|80\n"
        "1A|ignored|too|many|fields\n1A|BEE|60"
    )

    assert list(candidates) == [
        Answer(Id.across(1), "CAT", confidence_score=95),
        Answer(Id.across(1), "DOG", confidence_score=90),
        Answer(Id.across(1), "BEE", confidence_score=60),
    ]


def test_uses_no_match_for_a_candidate_with_an_invalid_score(converter):
    candidates = converter.to_candidates("2D|OWL|unknown")

    assert list(candidates) == [Answer.no_match(Id.down(2))]


def test_to_answer_uses_the_last_line_and_removes_whitespace(converter):
    answer = converter.to_answer("ignored prefix\n3A| New York | 87 ")

    assert answer == Answer(Id.across(3), "NEWYORK", confidence_score=87)


def test_rejects_candidate_with_invalid_answer_id(converter):
    with pytest.raises(ValueError, match="Invalid answer id"):
        converter.to_candidates("0A|CAT|90")
