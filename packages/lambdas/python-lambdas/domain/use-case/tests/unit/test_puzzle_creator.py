from types import SimpleNamespace
from unittest.mock import Mock

from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid

from crossword_solver_domain_use_case.puzzle_creator import PuzzleCreator


def test_create_downloads_image_and_extracts_clues_and_grid():
    image = SimpleNamespace(name="puzzle14", format=".jpg", hash="hash-value")
    clues = Clues([])
    grid = Grid(cells=Cells([]), column_width=10, row_height=10)
    image_downloader = Mock()
    image_downloader.download_image.return_value = image
    clue_extractor = Mock()
    clue_extractor.extract_clues.return_value = clues
    grid_extractor = Mock()
    grid_extractor.extract_grid.return_value = grid
    creator = PuzzleCreator(
        clue_extractor=clue_extractor,
        grid_extractor=grid_extractor,
        image_downloader=image_downloader,
    )

    puzzle = creator.create("https://example.com/puzzle14.jpg")

    image_downloader.download_image.assert_called_once_with("https://example.com/puzzle14.jpg")
    clue_extractor.extract_clues.assert_called_once_with(image)
    grid_extractor.extract_grid.assert_called_once_with(image)
    assert puzzle.name == "puzzle14"
    assert puzzle.format == ".jpg"
    assert puzzle.hash == "hash-value"
    assert puzzle.clues is clues
    assert puzzle.grid is grid
    assert puzzle.created_at.tzinfo is not None
