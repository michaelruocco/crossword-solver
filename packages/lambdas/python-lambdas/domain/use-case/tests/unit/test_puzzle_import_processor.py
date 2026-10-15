import logging
from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError
from crossword_solver_domain_use_case.puzzle_import_processor import PuzzleImportProcessor

IMAGE_URL = "https://example.com/puzzle.jpg"
CREATED_AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)
NOW = datetime(2026, 10, 15, 9, 31, tzinfo=UTC)


def an_import(status: PuzzleImportStatus = PuzzleImportStatus.PENDING) -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url=IMAGE_URL,
        status=status,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def a_processor(puzzle_import: PuzzleImport | None) -> tuple[PuzzleImportProcessor, Mock, Mock]:
    repository = Mock()
    repository.find_by_id.return_value = puzzle_import
    creator = Mock()
    return PuzzleImportProcessor(repository, creator, clock=lambda: NOW), repository, creator


def test_process_creates_puzzle_and_saves_import_as_complete():
    puzzle_import = an_import()
    puzzle_id = uuid4()
    processor, repository, creator = a_processor(puzzle_import)
    creator.create.return_value = puzzle_id

    processor.process(puzzle_import.id)

    creator.create.assert_called_once_with(IMAGE_URL)
    repository.save.assert_called_once_with(puzzle_import)
    assert puzzle_import.status == PuzzleImportStatus.COMPLETE
    assert puzzle_import.puzzle_id == puzzle_id
    assert puzzle_import.updated_at == NOW


def test_process_saves_import_as_failed_with_error_message_when_creation_fails(caplog):
    puzzle_import = an_import()
    processor, repository, creator = a_processor(puzzle_import)
    creator.create.side_effect = ValueError("No grid lines found")

    processor.process(puzzle_import.id)

    repository.save.assert_called_once_with(puzzle_import)
    assert puzzle_import.status == PuzzleImportStatus.FAILED
    assert puzzle_import.error == "No grid lines found"
    assert puzzle_import.puzzle_id is None
    assert puzzle_import.updated_at == NOW
    assert f"Failed to process puzzle import {puzzle_import.id}" in caplog.text


def test_process_uses_exception_type_as_error_when_it_has_no_message():
    puzzle_import = an_import()
    processor, _, creator = a_processor(puzzle_import)
    creator.create.side_effect = TimeoutError()

    processor.process(puzzle_import.id)

    assert puzzle_import.error == "TimeoutError"


@pytest.mark.parametrize("status", [PuzzleImportStatus.COMPLETE, PuzzleImportStatus.FAILED])
def test_process_skips_import_that_is_not_pending(status, caplog):
    puzzle_import = an_import(status)
    processor, repository, creator = a_processor(puzzle_import)

    with caplog.at_level(logging.INFO):
        processor.process(puzzle_import.id)

    creator.create.assert_not_called()
    repository.save.assert_not_called()
    assert puzzle_import.status == status
    assert f"Skipping puzzle import {puzzle_import.id} as its status is {status.value}" in caplog.text


def test_process_raises_error_when_import_not_found():
    import_id = uuid4()
    processor, repository, creator = a_processor(None)

    with pytest.raises(PuzzleImportNotFoundError):
        processor.process(import_id)

    creator.create.assert_not_called()
    repository.save.assert_not_called()


class _IdWithLineBreak(UUID):
    def __str__(self) -> str:
        return "id\nFAKE LOG ENTRY\r"


def test_process_removes_line_breaks_from_id_in_skipped_import_log(caplog):
    processor, _, _ = a_processor(an_import(PuzzleImportStatus.COMPLETE))

    with caplog.at_level(logging.INFO):
        processor.process(_IdWithLineBreak(int=1))

    assert "Skipping puzzle import idFAKE LOG ENTRY as its status is COMPLETE" in caplog.messages


def test_process_removes_line_breaks_from_id_in_failure_log(caplog):
    processor, _, creator = a_processor(an_import())
    creator.create.side_effect = ValueError("boom")

    processor.process(_IdWithLineBreak(int=1))

    assert "Failed to process puzzle import idFAKE LOG ENTRY" in caplog.messages
