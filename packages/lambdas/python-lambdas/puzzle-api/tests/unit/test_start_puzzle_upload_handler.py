from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus
from crossword_solver_domain_use_case.image_upload import ImageUpload
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_upload import PuzzleUpload
from crossword_solver_test_utils.responses import response_headers, response_json, response_status

from crossword_solver_puzzle_api.start_puzzle_upload import start_puzzle_upload_handler

NOW = datetime(2026, 10, 16, 9, 30, tzinfo=UTC)


def a_puzzle_upload() -> PuzzleUpload:
    puzzle_import = PuzzleImport(
        id=uuid4(),
        image_url="s3://puzzle-images/uploads/abc/puzzle14.png",
        status=PuzzleImportStatus.AWAITING_UPLOAD,
        created_at=NOW,
        updated_at=NOW,
    )
    upload = ImageUpload(
        image_url=puzzle_import.image_url,
        url="https://puzzle-images.s3.amazonaws.com/",
        fields={"key": "uploads/abc/puzzle14.png", "policy": "policy"},
    )
    return PuzzleUpload(puzzle_import, upload)


def test_handler_starts_upload_and_returns_created_with_the_upload_form(build_event, lambda_context):
    puzzle_upload = a_puzzle_upload()
    import_id = puzzle_upload.puzzle_import.id

    with patch.object(start_puzzle_upload_handler.puzzle_upload_starter, "start", return_value=puzzle_upload) as start:
        response = start_puzzle_upload_handler.lambda_handler(build_event({"fileName": "puzzle14.png"}), lambda_context)

    start.assert_called_once_with("puzzle14.png")
    assert response_status(response) == 201
    assert response_headers(response) == {
        "content-type": "application/json",
        "location": f"/v1/puzzles/imports/{import_id}",
    }
    assert response_json(response) == {
        "id": str(import_id),
        "status": "AWAITING_UPLOAD",
        "puzzleId": None,
        "puzzleUri": None,
        "error": None,
        "createdAt": "2026-10-16T09:30:00Z",
        "updatedAt": "2026-10-16T09:30:00Z",
        "upload": {
            "url": "https://puzzle-images.s3.amazonaws.com/",
            "fields": {"key": "uploads/abc/puzzle14.png", "policy": "policy"},
        },
    }


@pytest.mark.parametrize("body", [None, {}, {"fileName": ""}], ids=["no body", "no file name", "empty file name"])
def test_handler_returns_bad_request_for_invalid_request(build_event, lambda_context, body):
    with patch.object(start_puzzle_upload_handler.puzzle_upload_starter, "start") as start:
        response = start_puzzle_upload_handler.lambda_handler(build_event(body), lambda_context)

    start.assert_not_called()
    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid request"}


def test_handler_returns_unprocessable_entity_with_the_reason_when_the_file_is_invalid(build_event, lambda_context):
    error = InvalidImageError("image format gif is not an allowed format png,jpg,jpeg")

    with patch.object(start_puzzle_upload_handler.puzzle_upload_starter, "start", side_effect=error):
        response = start_puzzle_upload_handler.lambda_handler(build_event({"fileName": "puzzle.gif"}), lambda_context)

    assert response_status(response) == 422
    assert response_json(response) == {"message": "image format gif is not an allowed format png,jpg,jpeg"}


def test_handler_returns_internal_server_error_when_start_fails(build_event, lambda_context):
    with patch.object(start_puzzle_upload_handler.puzzle_upload_starter, "start", side_effect=RuntimeError("boom")):
        response = start_puzzle_upload_handler.lambda_handler(build_event({"fileName": "puzzle.png"}), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
