import threading
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cell_not_found_for_id_error import CellNotFoundForIdError
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.words import Words

from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_creator import PuzzleCreator

NOW = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


def an_image(name: str = "puzzle", image_format: str = ".png", image_hash: str = "hash") -> SimpleNamespace:
    return SimpleNamespace(name=name, format=image_format, hash=image_hash, bytes=b"image-bytes")


def test_create_downloads_image_extracts_clues_and_grid_and_saves_puzzle():
    image = an_image(name="puzzle14", image_format=".jpg", image_hash="hash-value")
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


def a_creator(clues: Clues, grid: Grid, repository: Mock, image=None, **kwargs) -> PuzzleCreator:
    image_downloader = Mock()
    image_downloader.download_image.return_value = image or an_image()
    clue_extractor = Mock()
    clue_extractor.extract_clues.return_value = clues
    grid_extractor = Mock()
    grid_extractor.extract_grid.return_value = grid
    return PuzzleCreator(clue_extractor, grid_extractor, image_downloader, repository, **kwargs)


def test_create_builds_words_from_the_clues_and_grid_cells():
    clues = Clues([Clue(Id.across(1), "clue (3)", [3])])
    grid = Grid(Cells([Cell(Coordinates(0, 2), black=False, id=1)]), 10, 10)
    repository = Mock()
    repository.find_by_hash.return_value = None

    a_creator(clues, grid, repository).create("https://example.com/puzzle.png")

    puzzle = repository.save.call_args.args[0]
    assert list(puzzle.words) == [Word(Id.across(1), 3, Coordinates(0, 2))]


def test_create_uses_given_words_factory():
    clues = Clues([])
    grid = Grid(Cells([]), 10, 10)
    words = Words([])
    words_factory = Mock()
    words_factory.to_words.return_value = words
    repository = Mock()
    repository.find_by_hash.return_value = None

    a_creator(clues, grid, repository, words_factory=words_factory).create("https://example.com/puzzle.png")

    words_factory.to_words.assert_called_once_with(clues, grid.cells)
    assert repository.save.call_args.args[0].words is words


def test_create_raises_error_and_saves_nothing_when_a_clue_has_no_cell():
    clues = Clues([Clue(Id.across(7), "clue (3)", [3])])
    grid = Grid(Cells([Cell(Coordinates(0, 2), black=False, id=1)]), 10, 10)
    repository = Mock()
    repository.find_by_hash.return_value = None
    creator = a_creator(clues, grid, repository)

    with pytest.raises(CellNotFoundForIdError):
        creator.create("https://example.com/puzzle.png")

    repository.save.assert_not_called()


def test_create_validates_the_downloaded_image():
    image = an_image(name="puzzle14")
    image_validator = Mock()
    repository = Mock()
    repository.find_by_hash.return_value = None
    creator = a_creator(Clues([]), Grid(Cells([]), 10, 10), repository, image=image, image_validator=image_validator)

    creator.create("https://example.com/puzzle.png")

    image_validator.validate.assert_called_once_with(image)


def test_create_looks_up_and_saves_nothing_when_the_image_is_invalid():
    image_validator = Mock()
    image_validator.validate.side_effect = InvalidImageError("image format gif is not an allowed format")
    repository = Mock()
    creator = a_creator(Clues([]), Grid(Cells([]), 10, 10), repository, image_validator=image_validator)

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        creator.create("https://example.com/puzzle.gif")

    repository.find_by_hash.assert_not_called()
    repository.save.assert_not_called()


def test_create_rejects_an_image_of_a_disallowed_format_by_default():
    repository = Mock()
    creator = a_creator(Clues([]), Grid(Cells([]), 10, 10), repository, image=an_image(image_format=".gif"))

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        creator.create("https://example.com/puzzle.gif")

    repository.save.assert_not_called()


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
    image_downloader.download_image.return_value = an_image()
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
    image_downloader.download_image.return_value = an_image(image_hash="known-hash")
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
    image_downloader.download_image.return_value = an_image()
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
