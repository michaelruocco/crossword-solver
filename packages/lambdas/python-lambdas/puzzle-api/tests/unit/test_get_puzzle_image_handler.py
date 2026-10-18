import base64
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.get_puzzle_image import get_puzzle_image_handler


def test_handler_returns_the_rendered_png(build_event, lambda_context):
    puzzle_id = uuid4()
    puzzle = MagicMock()
    image = b"png-bytes"

    with (
        patch.object(get_puzzle_image_handler.puzzle_finder, "find_by_id", return_value=puzzle) as find,
        patch.object(get_puzzle_image_handler.grid_image_factory, "to_png", return_value=image) as to_png,
    ):
        response = get_puzzle_image_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id)}), lambda_context
        )

    find.assert_called_once_with(puzzle_id)
    to_png.assert_called_once_with(puzzle.grid)
    assert response["statusCode"] == 200
    assert response["headers"] == {"content-type": "image/png"}
    assert response["isBase64Encoded"] is True
    assert base64.b64decode(response["body"]) == image


def test_handler_returns_not_found_when_puzzle_does_not_exist(build_event, lambda_context):
    puzzle_id = uuid4()

    with patch.object(get_puzzle_image_handler.puzzle_finder, "find_by_id", side_effect=PuzzleNotFoundError(puzzle_id)):
        response = get_puzzle_image_handler.lambda_handler(
            build_event(None, {"puzzleId": str(puzzle_id)}), lambda_context
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Puzzle not found"}


@pytest.mark.parametrize("path_parameters", [None, {}, {"puzzleId": "invalid"}])
def test_handler_returns_not_found_for_missing_or_invalid_id(build_event, lambda_context, path_parameters):
    with patch.object(get_puzzle_image_handler.puzzle_finder, "find_by_id") as find:
        response = get_puzzle_image_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    find.assert_not_called()
    assert response_status(response) == 404


def test_handler_returns_internal_server_error_when_image_rendering_fails(build_event, lambda_context):
    with (
        patch.object(get_puzzle_image_handler.puzzle_finder, "find_by_id", return_value=MagicMock()),
        patch.object(get_puzzle_image_handler.grid_image_factory, "to_png", side_effect=RuntimeError("boom")),
    ):
        response = get_puzzle_image_handler.lambda_handler(
            build_event(None, {"puzzleId": str(uuid4())}), lambda_context
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
