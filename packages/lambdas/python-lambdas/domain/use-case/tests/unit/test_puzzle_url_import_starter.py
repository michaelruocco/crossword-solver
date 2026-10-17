from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from crossword_solver_domain_entities.image_file import ImageFile
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_domain_use_case.image_validator import ImageValidator
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_url_import_starter import PuzzleUrlImportStarter

SOURCE_URL = "https://example.com/images/puzzle14.jpg"
FILE = ImageFile("puzzle14.jpg", b"image-bytes")
STORED_URL = "s3://bucket/images/abc/puzzle14.jpg"
NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def a_fetcher(file: ImageFile = FILE) -> Mock:
    fetcher = Mock()
    fetcher.fetch.return_value = file
    return fetcher


def a_store() -> Mock:
    store = Mock()
    store.save.return_value = STORED_URL
    return store


def a_starter(
    fetcher: Mock,
    store: Mock,
    repository: Mock | None = None,
    queue: Mock | None = None,
    validator: ImageValidator | None = None,
) -> PuzzleUrlImportStarter:
    return PuzzleUrlImportStarter(fetcher, store, repository or Mock(), queue or Mock(), validator, clock=lambda: NOW)


def test_start_fetches_validates_and_stores_the_image_then_saves_and_queues_a_pending_import():
    fetcher = a_fetcher()
    store = a_store()
    calls = []
    repository = Mock()
    repository.save.side_effect = lambda puzzle_import: calls.append(("save", puzzle_import.id))
    queue = Mock()
    queue.send.side_effect = lambda import_id: calls.append(("send", import_id))
    validator = Mock()
    validator.max_size_in_bytes = 1234

    puzzle_import = a_starter(fetcher, store, repository, queue, validator).start(SOURCE_URL)

    fetcher.fetch.assert_called_once_with(SOURCE_URL, 1234)
    validator.validate_file.assert_called_once_with(FILE)
    store.save.assert_called_once_with(FILE)
    assert puzzle_import.image_url == STORED_URL
    assert puzzle_import.source_url == SOURCE_URL
    assert puzzle_import.status == PuzzleImportStatus.PENDING
    assert puzzle_import.puzzle_id is None
    assert puzzle_import.created_at == NOW
    assert puzzle_import.updated_at == NOW
    assert calls == [("save", puzzle_import.id), ("send", puzzle_import.id)]


def test_start_limits_the_fetch_to_the_default_validators_maximum_size():
    fetcher = a_fetcher()

    a_starter(fetcher, a_store()).start(SOURCE_URL)

    fetcher.fetch.assert_called_once_with(SOURCE_URL, 20 * 1024 * 1024)


def test_start_stores_and_saves_nothing_when_the_image_cannot_be_fetched():
    fetcher = Mock()
    fetcher.fetch.side_effect = RuntimeError("boom")
    store = Mock()
    repository = Mock()
    starter = a_starter(fetcher, store, repository)

    with pytest.raises(RuntimeError, match="boom"):
        starter.start(SOURCE_URL)

    store.save.assert_not_called()
    repository.save.assert_not_called()


def test_start_stores_and_saves_nothing_when_the_image_is_invalid():
    fetcher = a_fetcher(ImageFile("puzzle14.gif", b"image-bytes"))
    store = Mock()
    repository = Mock()
    starter = a_starter(fetcher, store, repository)

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        starter.start(SOURCE_URL)

    store.save.assert_not_called()
    repository.save.assert_not_called()


def test_start_saves_no_import_when_the_image_cannot_be_stored():
    store = Mock()
    store.save.side_effect = RuntimeError("boom")
    repository = Mock()
    starter = a_starter(a_fetcher(), store, repository)

    with pytest.raises(RuntimeError, match="boom"):
        starter.start(SOURCE_URL)

    repository.save.assert_not_called()


def test_start_does_not_queue_when_the_import_cannot_be_saved():
    repository = Mock()
    repository.save.side_effect = RuntimeError("boom")
    queue = Mock()
    starter = a_starter(a_fetcher(), a_store(), repository, queue)

    with pytest.raises(RuntimeError, match="boom"):
        starter.start(SOURCE_URL)

    queue.send.assert_not_called()
