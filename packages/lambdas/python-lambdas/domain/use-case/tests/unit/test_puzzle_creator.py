import threading
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid

from crossword_solver_domain_use_case.puzzle_creator import PuzzleCreator

NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def test_create_downloads_image_extracts_clues_and_grid_and_saves_puzzle():
    image = SimpleNamespace(name="puzzle14", format=".jpg", hash="hash-value")
    clues = Clues([])
    grid = Grid(cells=Cells([]), column_width=10, row_height=10)
    image_downloader = Mock()
    image_downloader.download_image.return_value = image
    clue_extractor = Mock()
    clue_extractor.extract_clues.return_value = clues
    grid_extractor = Mock()
    grid_extractor.extract_grid.return_value = grid
    repository = Mock()
    repository.find_by_hash.return_value = None
    creator = PuzzleCreator(
        clue_extractor=clue_extractor,
        grid_extractor=grid_extractor,
        image_downloader=image_downloader,
        repository=repository,
        clock=lambda: NOW,
    )

    puzzle_id = creator.create("https://example.com/puzzle14.jpg")

    image_downloader.download_image.assert_called_once_with("https://example.com/puzzle14.jpg")
    clue_extractor.extract_clues.assert_called_once_with(image)
    grid_extractor.extract_grid.assert_called_once_with(image)
    repository.save.assert_called_once()
    puzzle = repository.save.call_args.args[0]
    assert puzzle.id == puzzle_id
    assert puzzle.name == "puzzle14"
    assert puzzle.format == ".jpg"
    assert puzzle.hash == "hash-value"
    assert puzzle.clues is clues
    assert puzzle.grid is grid
    assert puzzle.created_at == NOW


def test_create_extracts_clues_and_grid_at_the_same_time():
    # Each extractor waits for the other to start, which only succeeds if they run concurrently.
    both_started = threading.Barrier(2, timeout=5)
    clues = Clues([])
    grid = Grid(Cells([]), 10, 10)

    def extract_clues(image):
        both_started.wait()
        return clues

    def extract_grid(image):
        both_started.wait()
        return grid

    image_downloader = Mock()
    image_downloader.download_image.return_value = SimpleNamespace(name="puzzle", format=".png", hash="hash")
    clue_extractor = Mock()
    clue_extractor.extract_clues.side_effect = extract_clues
    grid_extractor = Mock()
    grid_extractor.extract_grid.side_effect = extract_grid
    repository = Mock()
    repository.find_by_hash.return_value = None
    creator = PuzzleCreator(clue_extractor, grid_extractor, image_downloader, repository)

    creator.create("https://example.com/puzzle.png")

    puzzle = repository.save.call_args.args[0]
    assert puzzle.clues is clues
    assert puzzle.grid is grid


def test_create_returns_existing_puzzle_id_without_extracting_when_hash_already_known():
    existing_id = uuid4()
    image_downloader = Mock()
    image_downloader.download_image.return_value = SimpleNamespace(name="puzzle", format=".png", hash="known-hash")
    clue_extractor = Mock()
    grid_extractor = Mock()
    repository = Mock()
    repository.find_by_hash.return_value = SimpleNamespace(id=existing_id)
    creator = PuzzleCreator(clue_extractor, grid_extractor, image_downloader, repository)

    puzzle_id = creator.create("https://example.com/puzzle.png")

    assert puzzle_id == existing_id
    repository.find_by_hash.assert_called_once_with("known-hash")
    clue_extractor.extract_clues.assert_not_called()
    grid_extractor.extract_grid.assert_not_called()
    repository.save.assert_not_called()


def test_create_raises_error_from_either_extractor():
    image_downloader = Mock()
    image_downloader.download_image.return_value = SimpleNamespace(name="puzzle", format=".png", hash="hash")
    clue_extractor = Mock()
    clue_extractor.extract_clues.return_value = Clues([])
    grid_extractor = Mock()
    grid_extractor.extract_grid.side_effect = ValueError("No grid lines found")
    repository = Mock()
    repository.find_by_hash.return_value = None
    creator = PuzzleCreator(clue_extractor, grid_extractor, image_downloader, repository)

    with pytest.raises(ValueError, match="No grid lines found"):
        creator.create("https://example.com/puzzle.png")

    repository.save.assert_not_called()
