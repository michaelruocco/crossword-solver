from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.create_attempt import create_attempt_handler


def test_handler_creates_and_reloads_attempt_then_returns_created_response(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    attempt = MagicMock()
    attempt_converter = MagicMock()
    attempt_converter.to_response.return_value.model_dump_json.return_value = '{"id":"attempt-id"}'

    with (
        patch.object(create_attempt_handler, "attempt_creator") as creator,
        patch.object(create_attempt_handler, "attempt_finder") as finder,
        patch.object(create_attempt_handler, "attempt_converter", attempt_converter),
    ):
        creator.create.return_value = attempt_id
        finder.find_by_id.return_value = attempt
        response = create_attempt_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id)}),
            lambda_context,
        )

    creator.create.assert_called_once_with(puzzle_id)
    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt_converter.to_response.assert_called_once_with(attempt)
    assert response == {
        "statusCode": 201,
        "headers": {"content-type": "application/json"},
        "body": '{"id":"attempt-id"}',
    }


@pytest.mark.parametrize("path_parameters", [None, {}, {"puzzleId": "not-a-uuid"}], ids=["none", "empty", "invalid"])
def test_handler_returns_not_found_for_missing_or_invalid_puzzle_id(build_event, lambda_context, path_parameters):
    with patch.object(create_attempt_handler, "attempt_creator") as creator:
        response = create_attempt_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    creator.create.assert_not_called()
    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


def test_handler_returns_not_found_when_puzzle_does_not_exist(build_event, lambda_context):
    puzzle_id = uuid4()
    with patch.object(create_attempt_handler.attempt_creator, "create", side_effect=PuzzleNotFoundError(puzzle_id)):
        event = build_event(None, {"puzzleId": str(puzzle_id)})
        response = create_attempt_handler.lambda_handler(event, lambda_context)

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


def test_handler_returns_not_found_when_created_attempt_cannot_be_reloaded(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    with (
        patch.object(create_attempt_handler.attempt_creator, "create", return_value=attempt_id),
        patch.object(
            create_attempt_handler.attempt_finder,
            "find_by_id",
            side_effect=AttemptNotFoundError(puzzle_id, attempt_id),
        ),
    ):
        event = build_event(None, {"puzzleId": str(puzzle_id)})
        response = create_attempt_handler.lambda_handler(event, lambda_context)

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Attempt not found"}


def test_handler_returns_internal_server_error_when_creation_fails(build_event, lambda_context):
    with patch.object(create_attempt_handler.attempt_creator, "create", side_effect=RuntimeError("boom")):
        response = create_attempt_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
