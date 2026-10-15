from unittest.mock import Mock
from uuid import uuid4

import pytest

from crossword_solver_domain_use_case.puzzle_import_finder import PuzzleImportFinder
from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError


def test_find_by_id_returns_import_from_repository():
    import_id = uuid4()
    puzzle_import = Mock()
    repository = Mock()
    repository.find_by_id.return_value = puzzle_import
    finder = PuzzleImportFinder(repository)

    assert finder.find_by_id(import_id) is puzzle_import
    repository.find_by_id.assert_called_once_with(import_id)


def test_find_by_id_raises_error_when_import_not_found():
    import_id = uuid4()
    repository = Mock()
    repository.find_by_id.return_value = None
    finder = PuzzleImportFinder(repository)

    with pytest.raises(PuzzleImportNotFoundError, match=f"Puzzle import not found with id {import_id}") as error:
        finder.find_by_id(import_id)

    assert error.value.import_id == import_id
