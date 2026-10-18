from unittest.mock import patch
from uuid import uuid4

from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.delete_puzzle import delete_puzzle_handler


def test_handler_deletes_puzzle_and_returns_no_content(build_event, lambda_context):
    puzzle_id = uuid4()

    with patch.object(delete_puzzle_handler.puzzle_deleter, "delete") as delete:
        response = delete_puzzle_handler.lambda_handler(build_event(None, {"puzzleId": str(puzzle_id)}), lambda_context)

    delete.assert_called_once_with(puzzle_id)
    assert response == {"statusCode": 204, "headers": {}, "body": ""}


def test_handler_returns_not_found_for_missing_or_invalid_id(build_event, lambda_context):
    for path_parameters in (None, {}, {"puzzleId": "invalid"}):
        with patch.object(delete_puzzle_handler.puzzle_deleter, "delete") as delete:
            response = delete_puzzle_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

        delete.assert_not_called()
        assert response_status(response) == 404
        assert response_json(response) == {"message": "Puzzle not found"}


def test_handler_returns_internal_server_error_when_delete_fails(build_event, lambda_context):
    with patch.object(delete_puzzle_handler.puzzle_deleter, "delete", side_effect=RuntimeError("boom")):
        response = delete_puzzle_handler.lambda_handler(build_event(None, {"puzzleId": str(uuid4())}), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
