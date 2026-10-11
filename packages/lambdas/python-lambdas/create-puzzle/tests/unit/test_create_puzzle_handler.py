import json
from unittest.mock import MagicMock, patch

from crossword_solver_create_puzzle.create_puzzle import create_puzzle_handler


def test_handler_returns_created_puzzle(build_event, lambda_context):
    image_url = "https://example.com/puzzle14.jpg"
    puzzle = MagicMock()
    event_converter = MagicMock()
    event_converter.to_request.return_value.image_url = image_url
    puzzle_converter = MagicMock()
    puzzle_converter.to_response.return_value.model_dump_json.return_value = '{"id": "puzzle-id"}'

    with (
        patch.object(create_puzzle_handler, "event_converter", event_converter),
        patch.object(create_puzzle_handler, "puzzle_converter", puzzle_converter),
        patch.object(create_puzzle_handler.puzzle_creator, "create", return_value=puzzle) as mock_create,
    ):
        response = create_puzzle_handler.lambda_handler(build_event({"imageUrl": image_url}), lambda_context)

    mock_create.assert_called_once_with(image_url)
    assert response == {
        "statusCode": 201,
        "headers": {"content-type": "application/json"},
        "body": '{"id": "puzzle-id"}',
    }


def test_handler_returns_internal_server_error_when_puzzle_creation_fails(build_event, lambda_context):
    image_url = "https://example.com/puzzle14.jpg"

    with patch.object(create_puzzle_handler.puzzle_creator, "create", side_effect=RuntimeError("boom")):
        response = create_puzzle_handler.lambda_handler(build_event({"imageUrl": image_url}), lambda_context)

    assert response == {
        "statusCode": 500,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"message": "Internal server error"}),
    }
