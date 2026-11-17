from unittest.mock import patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.get_candidate_answers import get_candidate_answers_handler


def test_returns_clue_and_confidence_sorted_answers(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    clue = Clue(Id.across(23), "Feline", [3], pattern="C??")
    candidates = Candidates(
        clue,
        [
            Answer(clue.id, "CAT", 75),
            Answer(clue.id, "COT", 95),
        ],
    )

    with (
        patch.object(get_candidate_answers_handler, "attempt_candidate_loader") as loader,
        patch.object(get_candidate_answers_handler, "candidate_answers_converter") as converter,
    ):
        loader.load_candidates.return_value = candidates
        converter.to_response.return_value.model_dump_json.return_value = (
            '{"clue":{"id":23,"direction":"ACROSS","text":"Feline","lengths":[3]},'
            '"answers":[{"id":"23A","value":"COT","confidenceScore":95},'
            '{"id":"23A","value":"CAT","confidenceScore":75}]}'
        )
        response = get_candidate_answers_handler.lambda_handler(
            build_event(
                None,
                {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id), "clueId": "23A"},
            ),
            lambda_context,
        )

    loader.load_candidates.assert_called_once_with(puzzle_id, attempt_id, Id.across(23))
    converter.to_response.assert_called_once_with(candidates)
    assert response_status(response) == 200
    assert response_json(response)["clue"]["id"] == 23
    assert [answer["confidenceScore"] for answer in response_json(response)["answers"]] == [95, 75]


@pytest.mark.parametrize(
    ("path_parameters", "expected_message"),
    [
        ({"puzzleId": "invalid", "attemptId": str(uuid4()), "clueId": "23A"}, "Invalid puzzle id"),
        ({"puzzleId": str(uuid4()), "attemptId": "invalid", "clueId": "23A"}, "Invalid attempt id"),
        ({"puzzleId": str(uuid4()), "attemptId": str(uuid4()), "clueId": "23X"}, "Invalid clue id"),
        ({"puzzleId": str(uuid4()), "attemptId": str(uuid4())}, "Invalid clue id"),
    ],
)
def test_returns_bad_request_for_invalid_path_parameters(
    build_event, lambda_context, path_parameters, expected_message
):
    with patch.object(get_candidate_answers_handler, "attempt_candidate_loader") as loader:
        response = get_candidate_answers_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    loader.load_candidates.assert_not_called()
    assert response_status(response) == 400
    assert response_json(response) == {"message": expected_message}


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_message"),
    [
        (AttemptNotFoundError(uuid4(), uuid4()), 404, "Attempt not found"),
        (PuzzleNotFoundError(uuid4()), 404, "Puzzle not found"),
        (ClueNotFoundForIdError(Id.across(23)), 404, "Clue not found"),
        (RuntimeError("boom"), 500, "Internal server error"),
    ],
)
def test_maps_lookup_errors_to_api_responses(build_event, lambda_context, error, expected_status, expected_message):
    with patch.object(get_candidate_answers_handler.attempt_candidate_loader, "load_candidates", side_effect=error):
        response = get_candidate_answers_handler.lambda_handler(
            build_event(
                None,
                {"puzzleId": str(uuid4()), "attemptId": str(uuid4()), "clueId": "23A"},
            ),
            lambda_context,
        )

    assert response_status(response) == expected_status
    assert response_json(response) == {"message": expected_message}
