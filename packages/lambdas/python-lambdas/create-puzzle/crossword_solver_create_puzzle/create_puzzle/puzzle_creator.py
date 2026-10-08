import uuid as uid
from datetime import UTC, datetime

from crossword_solver_domain_entities.puzzle import Puzzle

from .image.default_image_downloader import DefaultImageDownloader


class PuzzleCreator:
    def __init__(self, image_downloader: DefaultImageDownloader | None = None):
        self.image_downloader = image_downloader or DefaultImageDownloader()

    def create(self, image_url: str) -> Puzzle:
        image = self.image_downloader.download_image(image_url)
        return Puzzle(
            id=uid.uuid4(), name=image.name, format=image.format, hash=image.hash, created_at=datetime.now(UTC)
        )
