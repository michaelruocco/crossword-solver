from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_use_case.puzzle_service import PuzzleService


def test_create_delegates_to_creator():
    puzzle_id = uuid4()
    creator = Mock()
    creator.create.return_value = puzzle_id
    service = PuzzleService(creator=creator, finder=Mock())

    assert service.create("https://example.com/puzzle.png") == puzzle_id
    creator.create.assert_called_once_with("https://example.com/puzzle.png")


def test_find_by_id_delegates_to_finder():
    puzzle_id = uuid4()
    puzzle = Mock()
    finder = Mock()
    finder.find_by_id.return_value = puzzle
    service = PuzzleService(creator=Mock(), finder=finder)

    assert service.find_by_id(puzzle_id) is puzzle
    finder.find_by_id.assert_called_once_with(puzzle_id)
