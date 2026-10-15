import json
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus
from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError

from crossword_solver_create_puzzle.get_puzzle_import import get_puzzle_import_handler

NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def test_handler_returns_complete_import_with_puzzle_uri(build_event, lambda_context):
    import_id, puzzle_id = uuid4(), uuid4()
    puzzle_import = PuzzleImport(
        id=import_id,
        image_url="https://example.com/puzzle14.jpg",
        status=PuzzleImportStatus.COMPLETE,
        puzzle_id=puzzle_id,
        created_at=NOW,
        updated_at=NOW,
    )

    with patch.object(get_puzzle_import_handler.puzzle_import_finder, "find_by_id", return_value=puzzle_import) as find:
        response = get_puzzle_import_handler.lambda_handler(
            build_event(None, {"importId": str(import_id)}), lambda_context
        )

    find.assert_called_once_with(import_id)
    assert response["statusCode"] == 200
    assert response["headers"] == {"content-type": "application/json"}
    assert json.loads(response["body"]) == {
        "id": str(import_id),
        "status": "COMPLETE",
        "puzzleId": str(puzzle_id),
        "puzzleUri": f"/v1/puzzles/{puzzle_id}",
        "error": None,
        "createdAt": "2026-10-15T09:30:00Z",
        "updatedAt": "2026-10-15T09:30:00Z",
    }


def test_handler_returns_generic_error_for_failed_import(build_event, lambda_context):
    import_id = uuid4()
    puzzle_import = PuzzleImport(
        id=import_id,
        image_url="https://example.com/puzzle14.jpg",
        status=PuzzleImportStatus.FAILED,
        error="AccessDenied on arn:aws:dynamodb:eu-west-2:123456789012:table/puzzles",
        created_at=NOW,
        updated_at=NOW,
    )

    with patch.object(get_puzzle_import_handler.puzzle_import_finder, "find_by_id", return_value=puzzle_import):
        response = get_puzzle_import_handler.lambda_handler(
            build_event(None, {"importId": str(import_id)}), lambda_context
        )

    body = json.loads(response["body"])
    assert body["status"] == "FAILED"
    assert body["error"] == "Failed to import puzzle"
    assert "arn:aws" not in response["body"]


def test_handler_returns_not_found_when_import_does_not_exist(build_event, lambda_context):
    import_id = uuid4()

    with patch.object(
        get_puzzle_import_handler.puzzle_import_finder, "find_by_id", side_effect=PuzzleImportNotFoundError(import_id)
    ):
        response = get_puzzle_import_handler.lambda_handler(
            build_event(None, {"importId": str(import_id)}), lambda_context
        )

    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"message": "Puzzle import not found"}


@pytest.mark.parametrize("path_parameters", [None, {}, {"importId": "not-a-uuid"}], ids=["none", "empty", "invalid"])
def test_handler_returns_not_found_for_missing_or_invalid_import_id(build_event, lambda_context, path_parameters):
    with patch.object(get_puzzle_import_handler.puzzle_import_finder, "find_by_id") as find:
        response = get_puzzle_import_handler.lambda_handler(build_event(None, path_parameters), lambda_context)

    find.assert_not_called()
    assert response["statusCode"] == 404


def test_handler_returns_internal_server_error_when_find_fails(build_event, lambda_context):
    with patch.object(get_puzzle_import_handler.puzzle_import_finder, "find_by_id", side_effect=RuntimeError("boom")):
        response = get_puzzle_import_handler.lambda_handler(
            build_event(None, {"importId": str(uuid4())}), lambda_context
        )

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}
