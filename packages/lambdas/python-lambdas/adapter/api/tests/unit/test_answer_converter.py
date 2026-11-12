import pytest
from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id
from pydantic import ValidationError

from crossword_solver_adapter_api.answer_converter import AnswerConverter
from crossword_solver_adapter_api.answer_request import AnswerRequest


@pytest.mark.parametrize(
    ("clue_id", "expected_id"),
    [("3A", Id.across(3)), ("1D", Id.down(1))],
)
def test_converts_answer_request_to_domain_answer(clue_id, expected_id):
    answer = AnswerConverter().to_domain(AnswerRequest(id=clue_id, value="CAT"))

    assert answer == Answer(id=expected_id, value="CAT")


@pytest.mark.parametrize("clue_id", ["", "A3", "0A", "03A", "3X", "3a", "3A "])
def test_rejects_invalid_clue_id(clue_id):
    with pytest.raises(ValueError, match="clue id"):
        AnswerConverter().to_domain(AnswerRequest(id=clue_id, value="CAT"))


def test_request_requires_string_id_and_value():
    with pytest.raises(ValidationError):
        AnswerRequest.model_validate({"id": "3A", "value": None})


def test_converts_domain_answer_to_response():
    response = AnswerConverter().to_response(Answer(Id(3, Direction.ACROSS), "CAT"))

    assert response.model_dump() == {"id": "3A", "value": "CAT"}
