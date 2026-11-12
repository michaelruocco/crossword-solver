from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.get_attempt import get_attempt_handler


def test_handler_returns_attempt_response(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    attempt = MagicMock()
    attempt_converter = MagicMock()
    attempt_converter.to_response.return_value.model_dump_json.return_value = '{"id":"attempt-id"}'

    with (
        patch.object(get_attempt_handler, "attempt_finder") as finder,
        patch.object(get_attempt_handler, "attempt_converter", attempt_converter),
    ):
        finder.find_by_id.return_value = attempt
        response = get_attempt_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id)}),
            lambda_context,
        )

    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt_converter.to_response.assert_called_once_with(attempt)
    assert response == {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": '{"id":"attempt-id"}',
    }


@pytest.mark.parametrize(
    ("path_parameters", "expected_message"),
    [
        (None, "Puzzle not found"),
        ({}, "Puzzle not found"),
        ({"puzzleId": "not-a-uuid"}, "Puzzle not found"),
        ({"puzzleId": str(uuid4())}, "Attempt not found"),
        ({"puzzleId": str(uuid4()), "attemptId": "not-a-uuid"}, "Attempt not found"),
    ],
)
def test_handler_returns_not_found_for_missing_or_invalid_ids(
    build_event,
    lambda_context,
    path_parameters,
    expected_message,
):
    with patch.object(get_attempt_handler, "attempt_finder") as finder:
        response = get_attempt_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    finder.find_by_id.assert_not_called()
    assert response_status(response) == 404
    assert response_json(response) == {"message": expected_message}


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (AttemptNotFoundError(uuid4(), uuid4()), "Attempt not found"),
        (PuzzleNotFoundError(uuid4()), "Puzzle not found"),
    ],
)
def test_handler_maps_missing_resources_to_not_found(build_event, lambda_context, error, expected_message):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    with patch.object(get_attempt_handler.attempt_finder, "find_by_id", side_effect=error):
        response = get_attempt_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id)}),
            lambda_context,
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": expected_message}


def test_handler_returns_internal_server_error_when_lookup_fails(build_event, lambda_context):
    with patch.object(get_attempt_handler.attempt_finder, "find_by_id", side_effect=RuntimeError("boom")):
        response = get_attempt_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
