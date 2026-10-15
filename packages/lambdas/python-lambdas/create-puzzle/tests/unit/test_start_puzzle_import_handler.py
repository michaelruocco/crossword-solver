from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus
from crossword_solver_test_utils.responses import response_headers, response_json, response_status

from crossword_solver_create_puzzle.start_puzzle_import import start_puzzle_import_handler

IMAGE_URL = "https://example.com/puzzle14.jpg"
NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def a_pending_import() -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url=IMAGE_URL,
        status=PuzzleImportStatus.PENDING,
        created_at=NOW,
        updated_at=NOW,
    )


def test_handler_starts_import_and_returns_accepted_with_location(build_event, lambda_context):
    puzzle_import = a_pending_import()

    with patch.object(start_puzzle_import_handler.puzzle_import_starter, "start", return_value=puzzle_import) as start:
        response = start_puzzle_import_handler.lambda_handler(build_event({"imageUrl": IMAGE_URL}), lambda_context)

    start.assert_called_once_with(IMAGE_URL)
    assert response_status(response) == 202
    assert response_headers(response) == {
        "content-type": "application/json",
        "location": f"/v1/puzzles/imports/{puzzle_import.id}",
    }
    assert response_json(response) == {
        "id": str(puzzle_import.id),
        "status": "PENDING",
        "puzzleId": None,
        "puzzleUri": None,
        "error": None,
        "createdAt": "2026-10-15T09:30:00Z",
        "updatedAt": "2026-10-15T09:30:00Z",
    }


@pytest.mark.parametrize(
    "body",
    [None, {}, {"imageUrl": "file:///etc/passwd"}, {"imageUrl": "not a url"}],
    ids=["no body", "no image url", "file url", "not a url"],
)
def test_handler_returns_bad_request_for_invalid_request(build_event, lambda_context, body):
    with patch.object(start_puzzle_import_handler.puzzle_import_starter, "start") as start:
        response = start_puzzle_import_handler.lambda_handler(build_event(body), lambda_context)

    start.assert_not_called()
    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid request"}


def test_handler_returns_internal_server_error_when_start_fails(build_event, lambda_context):
    with patch.object(start_puzzle_import_handler.puzzle_import_starter, "start", side_effect=RuntimeError("boom")):
        response = start_puzzle_import_handler.lambda_handler(build_event({"imageUrl": IMAGE_URL}), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
