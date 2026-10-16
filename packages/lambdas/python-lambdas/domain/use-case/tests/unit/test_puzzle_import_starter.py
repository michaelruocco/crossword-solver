from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_domain_use_case.puzzle_import_starter import PuzzleImportStarter

IMAGE_URL = "https://example.com/puzzle.jpg"
NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def test_start_saves_pending_import_then_queues_its_id():
    calls = []
    repository = Mock()
    repository.save.side_effect = lambda puzzle_import: calls.append(("save", puzzle_import.id))
    queue = Mock()
    queue.send.side_effect = lambda import_id: calls.append(("send", import_id))
    starter = PuzzleImportStarter(repository, queue, clock=lambda: NOW)

    puzzle_import = starter.start(IMAGE_URL)

    assert puzzle_import.image_url == IMAGE_URL
    assert puzzle_import.source_url is None
    assert puzzle_import.status == PuzzleImportStatus.PENDING
    assert puzzle_import.puzzle_id is None
    assert puzzle_import.created_at == NOW
    assert puzzle_import.updated_at == NOW
    assert calls == [("save", puzzle_import.id), ("send", puzzle_import.id)]


def test_start_keeps_the_source_url_when_given():
    starter = PuzzleImportStarter(Mock(), Mock(), clock=lambda: NOW)

    puzzle_import = starter.start("s3://bucket/uploads/abc/puzzle.jpg", source_url=IMAGE_URL)

    assert puzzle_import.image_url == "s3://bucket/uploads/abc/puzzle.jpg"
    assert puzzle_import.source_url == IMAGE_URL


def test_start_does_not_queue_when_save_fails():
    repository = Mock()
    repository.save.side_effect = RuntimeError("boom")
    queue = Mock()
    starter = PuzzleImportStarter(repository, queue)

    with pytest.raises(RuntimeError, match="boom"):
        starter.start(IMAGE_URL)

    queue.send.assert_not_called()
