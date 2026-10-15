from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_use_case.puzzle_import_service import PuzzleImportService


def test_start_delegates_to_starter():
    puzzle_import = Mock()
    starter = Mock()
    starter.start.return_value = puzzle_import
    service = PuzzleImportService(starter=starter, finder=Mock(), processor=Mock())

    assert service.start("https://example.com/puzzle.jpg") is puzzle_import
    starter.start.assert_called_once_with("https://example.com/puzzle.jpg")


def test_find_by_id_delegates_to_finder():
    import_id = uuid4()
    puzzle_import = Mock()
    finder = Mock()
    finder.find_by_id.return_value = puzzle_import
    service = PuzzleImportService(starter=Mock(), finder=finder, processor=Mock())

    assert service.find_by_id(import_id) is puzzle_import
    finder.find_by_id.assert_called_once_with(import_id)


def test_process_delegates_to_processor():
    import_id = uuid4()
    processor = Mock()
    service = PuzzleImportService(starter=Mock(), finder=Mock(), processor=processor)

    service.process(import_id)

    processor.process.assert_called_once_with(import_id)
