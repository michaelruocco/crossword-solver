from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_domain_use_case.image_upload import ImageUpload
from crossword_solver_domain_use_case.image_validator import ImageValidator
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_upload_starter import PuzzleUploadStarter

NOW = datetime(2026, 10, 16, 9, 30, tzinfo=UTC)
UPLOAD = ImageUpload(
    image_url="s3://bucket/uploads/abc/puzzle.png",
    url="https://bucket.s3.amazonaws.com/",
    fields={"key": "uploads/abc/puzzle.png"},
)


def test_start_saves_an_import_awaiting_upload_and_returns_the_upload():
    repository = Mock()
    upload_store = Mock()
    upload_store.create_upload.return_value = UPLOAD
    starter = PuzzleUploadStarter(repository, upload_store, ImageValidator(max_size_in_mb=1), clock=lambda: NOW)

    result = starter.start("puzzle.png")

    puzzle_import = result.puzzle_import
    upload_store.create_upload.assert_called_once_with(puzzle_import.id, "puzzle.png", 1024 * 1024)
    repository.save.assert_called_once_with(puzzle_import)
    assert result.upload == UPLOAD
    assert puzzle_import.image_url == UPLOAD.image_url
    assert puzzle_import.status == PuzzleImportStatus.AWAITING_UPLOAD
    assert puzzle_import.source_url is None
    assert puzzle_import.created_at == NOW
    assert puzzle_import.updated_at == NOW


def test_start_rejects_a_file_that_is_not_an_allowed_format():
    repository = Mock()
    upload_store = Mock()
    starter = PuzzleUploadStarter(repository, upload_store)

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        starter.start("puzzle.gif")

    upload_store.create_upload.assert_not_called()
    repository.save.assert_not_called()
