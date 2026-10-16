import uuid as uid
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.words_factory import WordsFactory

from .clock import Clock, system_clock
from .clue_extractor import ClueExtractor
from .grid_extractor import GridExtractor
from .image_downloader import ImageDownloader
from .image_validator import ImageValidator
from .puzzle_repository import PuzzleRepository


class PuzzleCreator:
    def __init__(
        self,
        clue_extractor: ClueExtractor,
        grid_extractor: GridExtractor,
        image_downloader: ImageDownloader,
        repository: PuzzleRepository,
        clock: Clock = system_clock,
        words_factory: WordsFactory | None = None,
        image_validator: ImageValidator | None = None,
    ):
        self.image_downloader = image_downloader
        self.clue_extractor = clue_extractor
        self.grid_extractor = grid_extractor
        self.repository = repository
        self.clock = clock
        self.words_factory = words_factory or WordsFactory()
        self.image_validator = image_validator or ImageValidator()

    def create(self, image_url: str) -> UUID:
        image = self.image_downloader.download_image(image_url)
        self.image_validator.validate(image)
        existing = self.repository.find_by_hash(image.hash)
        if existing is not None:
            return existing.id
        # Bedrock waits on the network while grid extraction runs OCR, so threads let them overlap.
        with ThreadPoolExecutor(max_workers=2) as executor:
            clues_future = executor.submit(self.clue_extractor.extract_clues, image)
            grid_future = executor.submit(self.grid_extractor.extract_grid, image)
            clues = clues_future.result()
            grid = grid_future.result()
            puzzle = Puzzle(
                id=uid.uuid4(),
                name=image.name,
                format=image.format,
                hash=image.hash,
                clues=clues,
                grid=grid,
                words=self.words_factory.to_words(clues, grid.cells),
                created_at=self.clock(),
            )
        self.repository.save(puzzle)
        return puzzle.id
