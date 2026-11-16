from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.delete_attempt_answer import delete_attempt_answer_handler


def test_handler_deletes_answer_and_returns_updated_attempt(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    attempt = MagicMock()
    attempt_converter = MagicMock()
    attempt_converter.to_response.return_value.model_dump_json.return_value = '{"id":"attempt-id","answerCount":0}'

    with (
        patch.object(delete_attempt_answer_handler, "attempt_answer_service") as service,
        patch.object(delete_attempt_answer_handler, "attempt_converter", attempt_converter),
    ):
        service.delete_answer.return_value = attempt
        response = delete_attempt_answer_handler.lambda_handler(
            build_event(
                None,
                {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id), "answerId": "23D"},
            ),
            lambda_context,
        )

    service.delete_answer.assert_called_once_with(puzzle_id, attempt_id, Id.down(23))
    attempt_converter.to_response.assert_called_once_with(attempt)
    assert response_status(response) == 200
    assert response_json(response) == {"id": "attempt-id", "answerCount": 0}


@pytest.mark.parametrize(
    ("path_parameters", "expected_message"),
    [
        ({"puzzleId": "invalid", "attemptId": str(uuid4()), "answerId": "23D"}, "Invalid puzzle id"),
        ({"puzzleId": str(uuid4()), "attemptId": "invalid", "answerId": "23D"}, "Invalid attempt id"),
        ({"attemptId": str(uuid4()), "answerId": "23D"}, "Invalid puzzle id"),
        ({"puzzleId": str(uuid4()), "answerId": "23D"}, "Invalid attempt id"),
    ],
)
def test_handler_returns_bad_request_for_invalid_or_missing_puzzle_or_attempt_id(
    build_event, lambda_context, path_parameters, expected_message
):
    with patch.object(delete_attempt_answer_handler, "attempt_answer_service") as service:
        response = delete_attempt_answer_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    service.delete_answer.assert_not_called()
    assert response_status(response) == 400
    assert response_json(response) == {"message": expected_message}


@pytest.mark.parametrize("answer_id", ["", "23X", "023D"])
def test_handler_returns_bad_request_for_invalid_answer_id(build_event, lambda_context, answer_id):
    response = delete_attempt_answer_handler.lambda_handler(
        build_event(None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4()), "answerId": answer_id}),
        lambda_context,
    )

    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid answer id"}


def test_handler_returns_bad_request_when_answer_id_is_missing(build_event, lambda_context):
    response = delete_attempt_answer_handler.lambda_handler(
        build_event(None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
        lambda_context,
    )

    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid answer id"}


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (AttemptNotFoundError(uuid4(), uuid4()), "Attempt not found"),
        (PuzzleNotFoundError(uuid4()), "Puzzle not found"),
    ],
)
def test_handler_maps_missing_resources_to_not_found(build_event, lambda_context, error, expected_message):
    with patch.object(delete_attempt_answer_handler.attempt_answer_service, "delete_answer", side_effect=error):
        response = delete_attempt_answer_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4()), "answerId": "23D"}),
            lambda_context,
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": expected_message}


def test_handler_returns_internal_server_error_when_delete_fails(build_event, lambda_context):
    with patch.object(
        delete_attempt_answer_handler.attempt_answer_service,
        "delete_answer",
        side_effect=RuntimeError("boom"),
    ):
        response = delete_attempt_answer_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4()), "answerId": "23D"}),
            lambda_context,
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
