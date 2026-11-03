from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.get_attempt_summaries import get_attempt_summaries_handler


def test_handler_returns_attempt_summaries(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt = MagicMock()
    summary_response = MagicMock()
    summary_response.model_dump.return_value = {
        "id": "attempt-id",
        "createdAt": "2026-10-31T09:30:00Z",
        "solving": True,
        "answerCount": 3,
        "clueCount": 24,
    }

    with (
        patch.object(
            get_attempt_summaries_handler.attempt_lister, "list_by_puzzle_id", return_value=[attempt]
        ) as lister,
        patch.object(
            get_attempt_summaries_handler.attempt_summary_converter,
            "to_response",
            return_value=summary_response,
        ) as converter,
    ):
        response = get_attempt_summaries_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id)}),
            lambda_context,
        )

    lister.assert_called_once_with(puzzle_id)
    converter.assert_called_once_with(attempt)
    assert response_status(response) == 200
    assert response_json(response) == [summary_response.model_dump.return_value]


@pytest.mark.parametrize("path_parameters", [None, {}, {"puzzleId": "not-a-uuid"}], ids=["none", "empty", "invalid"])
def test_handler_returns_not_found_for_missing_or_invalid_puzzle_id(build_event, lambda_context, path_parameters):
    with patch.object(get_attempt_summaries_handler.attempt_lister, "list_by_puzzle_id") as lister:
        response = get_attempt_summaries_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    lister.assert_not_called()
    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


def test_handler_returns_empty_array_when_puzzle_has_no_attempts(build_event, lambda_context):
    with patch.object(get_attempt_summaries_handler.attempt_lister, "list_by_puzzle_id", return_value=[]):
        response = get_attempt_summaries_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 200
    assert response_json(response) == []


def test_handler_returns_not_found_when_puzzle_does_not_exist(build_event, lambda_context):
    puzzle_id = uuid4()
    with patch.object(
        get_attempt_summaries_handler.attempt_lister,
        "list_by_puzzle_id",
        side_effect=PuzzleNotFoundError(puzzle_id),
    ):
        response = get_attempt_summaries_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id)}),
            lambda_context,
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


def test_handler_returns_internal_server_error_when_listing_fails(build_event, lambda_context):
    with patch.object(
        get_attempt_summaries_handler.attempt_lister,
        "list_by_puzzle_id",
        side_effect=RuntimeError("boom"),
    ):
        response = get_attempt_summaries_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
