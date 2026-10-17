from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_use_case.puzzle_deleter import PuzzleDeleter


def test_delete_delegates_to_the_repository():
    puzzle_id = uuid4()
    repository = Mock()
    deleter = PuzzleDeleter(repository)

    deleter.delete(puzzle_id)

    repository.delete_by_id.assert_called_once_with(puzzle_id)
