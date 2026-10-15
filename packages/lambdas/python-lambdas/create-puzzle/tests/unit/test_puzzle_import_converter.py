from datetime import UTC, datetime
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_create_puzzle.puzzle_import.puzzle_import_converter import PuzzleImportConverter

NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)
LATER = datetime(2026, 10, 15, 9, 31, tzinfo=UTC)


def an_import(status: PuzzleImportStatus, **kwargs) -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url="https://example.com/puzzle.jpg",
        status=status,
        created_at=NOW,
        updated_at=LATER,
        **kwargs,
    )


@pytest.fixture
def converter() -> PuzzleImportConverter:
    return PuzzleImportConverter()


def test_to_response_for_pending_import(converter):
    puzzle_import = an_import(PuzzleImportStatus.PENDING)

    response = converter.to_response(puzzle_import)

    assert response.id == puzzle_import.id
    assert response.status == "PENDING"
    assert response.puzzle_id is None
    assert response.puzzle_uri is None
    assert response.error is None
    assert response.created_at == NOW
    assert response.updated_at == LATER


def test_to_response_for_complete_import_links_to_puzzle(converter):
    puzzle_id = uuid4()

    response = converter.to_response(an_import(PuzzleImportStatus.COMPLETE, puzzle_id=puzzle_id))

    assert response.status == "COMPLETE"
    assert response.puzzle_id == puzzle_id
    assert response.puzzle_uri == f"/v1/puzzles/{puzzle_id}"
    assert response.error is None


def test_to_response_for_failed_import_hides_stored_error(converter):
    response = converter.to_response(an_import(PuzzleImportStatus.FAILED, error="internal detail"))

    assert response.status == "FAILED"
    assert response.error == "Failed to import puzzle"
    assert response.puzzle_uri is None


def test_to_location_is_uri_of_import(converter):
    puzzle_import = an_import(PuzzleImportStatus.PENDING)

    assert converter.to_location(puzzle_import) == f"/v1/puzzles/imports/{puzzle_import.id}"
