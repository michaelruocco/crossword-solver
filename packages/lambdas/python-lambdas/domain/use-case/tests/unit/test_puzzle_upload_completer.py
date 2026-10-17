from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError
from crossword_solver_domain_use_case.puzzle_upload_completer import PuzzleUploadCompleter

CREATED_AT = datetime(2026, 10, 16, 9, 30, tzinfo=UTC)
NOW = datetime(2026, 10, 16, 9, 31, tzinfo=UTC)


def an_import(status: PuzzleImportStatus) -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url="s3://bucket/uploads/abc/puzzle.png",
        status=status,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def test_complete_marks_the_import_pending_then_queues_it():
    puzzle_import = an_import(PuzzleImportStatus.AWAITING_UPLOAD)
    calls = []
    repository = Mock()
    repository.find_by_id.return_value = puzzle_import
    repository.save.side_effect = lambda saved: calls.append(("save", saved.status))
    queue = Mock()
    queue.send.side_effect = lambda import_id: calls.append(("send", import_id))
    completer = PuzzleUploadCompleter(repository, queue, clock=lambda: NOW)

    completer.complete(puzzle_import.id)

    repository.find_by_id.assert_called_once_with(puzzle_import.id)
    assert calls == [("save", PuzzleImportStatus.PENDING), ("send", puzzle_import.id)]
    assert puzzle_import.updated_at == NOW


@pytest.mark.parametrize("status", [PuzzleImportStatus.PENDING, PuzzleImportStatus.COMPLETE, PuzzleImportStatus.FAILED])
def test_complete_skips_an_import_that_is_not_awaiting_upload(status):
    puzzle_import = an_import(status)
    repository = Mock()
    repository.find_by_id.return_value = puzzle_import
    queue = Mock()

    PuzzleUploadCompleter(repository, queue).complete(puzzle_import.id)

    repository.save.assert_not_called()
    queue.send.assert_not_called()
    assert puzzle_import.status == status


def test_complete_raises_error_when_the_import_does_not_exist():
    repository = Mock()
    repository.find_by_id.return_value = None
    completer = PuzzleUploadCompleter(repository, Mock())
    import_id = uuid4()

    with pytest.raises(PuzzleImportNotFoundError):
        completer.complete(import_id)
