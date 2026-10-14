import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

from crossword_solver_create_puzzle.create_puzzle import create_puzzle_handler


def test_handler_returns_created_puzzle(build_event, lambda_context):
    image_url = "https://example.com/puzzle14.jpg"
    puzzle_id = uuid4()
    puzzle = MagicMock()
    event_converter = MagicMock()
    event_converter.to_request.return_value.image_url = image_url
    puzzle_converter = MagicMock()
    puzzle_converter.to_response.return_value.model_dump_json.return_value = '{"id": "puzzle-id"}'

    with (
        patch.object(create_puzzle_handler, "event_converter", event_converter),
        patch.object(create_puzzle_handler, "puzzle_converter", puzzle_converter),
        patch.object(create_puzzle_handler.puzzle_service, "create", return_value=puzzle_id) as mock_create,
        patch.object(create_puzzle_handler.puzzle_service, "find_by_id", return_value=puzzle) as mock_find_by_id,
    ):
        response = create_puzzle_handler.lambda_handler(build_event({"imageUrl": image_url}), lambda_context)

    mock_create.assert_called_once_with(image_url)
    mock_find_by_id.assert_called_once_with(puzzle_id)
    puzzle_converter.to_response.assert_called_once_with(puzzle)
    assert response == {
        "statusCode": 201,
        "headers": {"content-type": "application/json"},
        "body": '{"id": "puzzle-id"}',
    }


def test_handler_returns_internal_server_error_when_puzzle_creation_fails(build_event, lambda_context):
    image_url = "https://example.com/puzzle14.jpg"

    with patch.object(create_puzzle_handler.puzzle_service, "create", side_effect=RuntimeError("boom")):
        response = create_puzzle_handler.lambda_handler(build_event({"imageUrl": image_url}), lambda_context)

    assert response == {
        "statusCode": 500,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"message": "Internal server error"}),
    }
