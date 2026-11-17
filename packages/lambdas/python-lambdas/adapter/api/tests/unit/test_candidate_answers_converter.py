from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.id import Id

from crossword_solver_adapter_api.candidate_answers_converter import CandidateAnswersConverter


def test_converts_clue_and_sorts_answers_by_confidence_descending():
    clue = Clue(Id.across(23), "Feline", [3], pattern="C??")
    candidates = Candidates(
        clue,
        [
            Answer(clue.id, "CAT", 75),
            Answer(clue.id, "COT", 95),
            Answer(clue.id, "CUT", 85),
        ],
    )

    response = CandidateAnswersConverter().to_response(candidates)

    assert response.model_dump(by_alias=True) == {
        "clue": {"id": 23, "direction": "ACROSS", "text": "Feline", "lengths": [3]},
        "answers": [
            {"id": "23A", "value": "COT", "confidenceScore": 95},
            {"id": "23A", "value": "CUT", "confidenceScore": 85},
            {"id": "23A", "value": "CAT", "confidenceScore": 75},
        ],
    }


def test_converts_empty_candidates_to_empty_answer_array():
    clue = Clue(Id.across(23), "Feline", [3])

    response = CandidateAnswersConverter().to_response(Candidates(clue))

    assert response.answers == []
