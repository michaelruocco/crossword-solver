from datetime import UTC, datetime
from uuid import uuid4

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

CREATED_AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)
LATER = datetime(2026, 10, 15, 9, 31, tzinfo=UTC)


def a_pending_import() -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url="https://example.com/puzzle.jpg",
        status=PuzzleImportStatus.PENDING,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def test_upload_received_sets_status_pending_and_updated_at():
    puzzle_import = a_pending_import()
    puzzle_import.status = PuzzleImportStatus.AWAITING_UPLOAD

    puzzle_import.upload_received(LATER)

    assert puzzle_import.status == PuzzleImportStatus.PENDING
    assert puzzle_import.updated_at == LATER
    assert puzzle_import.created_at == CREATED_AT


def test_complete_sets_status_puzzle_id_and_updated_at():
    puzzle_import = a_pending_import()
    puzzle_id = uuid4()

    puzzle_import.complete(puzzle_id, LATER)

    assert puzzle_import.status == PuzzleImportStatus.COMPLETE
    assert puzzle_import.puzzle_id == puzzle_id
    assert puzzle_import.error is None
    assert puzzle_import.updated_at == LATER
    assert puzzle_import.created_at == CREATED_AT


def test_fail_sets_status_error_and_updated_at():
    puzzle_import = a_pending_import()

    puzzle_import.fail("Failed to download image", LATER)

    assert puzzle_import.status == PuzzleImportStatus.FAILED
    assert puzzle_import.error == "Failed to download image"
    assert puzzle_import.puzzle_id is None
    assert puzzle_import.updated_at == LATER
