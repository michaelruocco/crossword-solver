import uuid as uid
from datetime import UTC, datetime

from crossword_solver_domain_entities.puzzle import Puzzle

from .clue_extractor import ClueExtractor
from .grid_extractor import GridExtractor
from .image_downloader import ImageDownloader


class PuzzleCreator:
    def __init__(
        self,
        clue_extractor: ClueExtractor,
        grid_extractor: GridExtractor,
        image_downloader: ImageDownloader,
    ):
        self.image_downloader = image_downloader
        self.clue_extractor = clue_extractor
        self.grid_extractor = grid_extractor

    def create(self, image_url: str) -> Puzzle:
        image = self.image_downloader.download_image(image_url)
        clues = self.clue_extractor.extract_clues(image)
        grid = self.grid_extractor.extract_grid(image)
        return Puzzle(
            id=uid.uuid4(),
            name=image.name,
            format=image.format,
            hash=image.hash,
            clues=clues,
            grid=grid,
            created_at=datetime.now(UTC),
        )
