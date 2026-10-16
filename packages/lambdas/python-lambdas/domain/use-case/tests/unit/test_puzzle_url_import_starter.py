from unittest.mock import Mock

import pytest

from crossword_solver_domain_use_case.image_file import ImageFile
from crossword_solver_domain_use_case.image_validator import ImageValidator
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_url_import_starter import PuzzleUrlImportStarter

SOURCE_URL = "https://example.com/images/puzzle14.jpg"
FILE = ImageFile("puzzle14.jpg", b"image-bytes")
STORED_URL = "s3://bucket/uploads/abc/puzzle14.jpg"


def a_starter(fetcher: Mock, store: Mock, starter: Mock, validator: ImageValidator | None = None):
    return PuzzleUrlImportStarter(fetcher, store, starter, validator)


def test_start_fetches_validates_stores_then_starts_an_import_keeping_the_source_url():
    puzzle_import = Mock()
    fetcher = Mock()
    fetcher.fetch.return_value = FILE
    store = Mock()
    store.save.return_value = STORED_URL
    starter = Mock()
    starter.start.return_value = puzzle_import
    validator = Mock()
    validator.max_size_in_bytes = 1234

    result = a_starter(fetcher, store, starter, validator).start(SOURCE_URL)

    assert result is puzzle_import
    fetcher.fetch.assert_called_once_with(SOURCE_URL, 1234)
    validator.validate_file.assert_called_once_with(FILE)
    store.save.assert_called_once_with(FILE)
    starter.start.assert_called_once_with(STORED_URL, source_url=SOURCE_URL)


def test_start_limits_the_fetch_to_the_default_validators_maximum_size():
    fetcher = Mock()
    fetcher.fetch.return_value = FILE
    url_import_starter = a_starter(fetcher, Mock(), Mock())

    url_import_starter.start(SOURCE_URL)

    fetcher.fetch.assert_called_once_with(SOURCE_URL, 20 * 1024 * 1024)


def test_start_stores_and_starts_nothing_when_the_image_cannot_be_fetched():
    fetcher = Mock()
    fetcher.fetch.side_effect = RuntimeError("boom")
    store = Mock()
    starter = Mock()
    url_import_starter = a_starter(fetcher, store, starter)

    with pytest.raises(RuntimeError, match="boom"):
        url_import_starter.start(SOURCE_URL)

    store.save.assert_not_called()
    starter.start.assert_not_called()


def test_start_stores_and_starts_nothing_when_the_image_is_invalid():
    fetcher = Mock()
    fetcher.fetch.return_value = ImageFile("puzzle14.gif", b"image-bytes")
    store = Mock()
    starter = Mock()
    url_import_starter = a_starter(fetcher, store, starter)

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        url_import_starter.start(SOURCE_URL)

    store.save.assert_not_called()
    starter.start.assert_not_called()


def test_start_starts_no_import_when_the_image_cannot_be_stored():
    fetcher = Mock()
    fetcher.fetch.return_value = FILE
    store = Mock()
    store.save.side_effect = RuntimeError("boom")
    starter = Mock()
    url_import_starter = a_starter(fetcher, store, starter)

    with pytest.raises(RuntimeError, match="boom"):
        url_import_starter.start(SOURCE_URL)

    starter.start.assert_not_called()
