from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_create_puzzle.get_puzzle import get_puzzle_handler


def test_handler_returns_puzzle(build_event, lambda_context):
    puzzle_id = uuid4()
    puzzle = MagicMock()
    puzzle_converter = MagicMock()
    puzzle_converter.to_response.return_value.model_dump_json.return_value = '{"id": "puzzle-id"}'

    with (
        patch.object(get_puzzle_handler, "puzzle_converter", puzzle_converter),
        patch.object(get_puzzle_handler.puzzle_finder, "find_by_id", return_value=puzzle) as find,
    ):
        response = get_puzzle_handler.lambda_handler(build_event(None, {"puzzleId": str(puzzle_id)}), lambda_context)

    find.assert_called_once_with(puzzle_id)
    puzzle_converter.to_response.assert_called_once_with(puzzle)
    assert response == {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": '{"id": "puzzle-id"}',
    }


def test_handler_returns_not_found_when_puzzle_does_not_exist(build_event, lambda_context):
    puzzle_id = uuid4()

    with patch.object(get_puzzle_handler.puzzle_finder, "find_by_id", side_effect=PuzzleNotFoundError(puzzle_id)):
        response = get_puzzle_handler.lambda_handler(build_event(None, {"puzzleId": str(puzzle_id)}), lambda_context)

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


@pytest.mark.parametrize("path_parameters", [None, {}, {"puzzleId": "not-a-uuid"}], ids=["none", "empty", "invalid"])
def test_handler_returns_not_found_for_missing_or_invalid_puzzle_id(build_event, lambda_context, path_parameters):
    with patch.object(get_puzzle_handler.puzzle_finder, "find_by_id") as find:
        response = get_puzzle_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    find.assert_not_called()
    assert response_status(response) == 404


def test_handler_returns_internal_server_error_when_find_fails(build_event, lambda_context):
    with patch.object(get_puzzle_handler.puzzle_finder, "find_by_id", side_effect=RuntimeError("boom")):
        response = get_puzzle_handler.lambda_handler(build_event(None, {"puzzleId": str(uuid4())}), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
