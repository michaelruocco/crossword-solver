from uuid import UUID

from crossword_solver_domain_entities.puzzle_import import PuzzleImport

from .puzzle_import_finder import PuzzleImportFinder
from .puzzle_import_processor import PuzzleImportProcessor
from .puzzle_import_starter import PuzzleImportStarter


class PuzzleImportService:
    def __init__(
        self,
        starter: PuzzleImportStarter,
        finder: PuzzleImportFinder,
        processor: PuzzleImportProcessor,
    ):
        self.starter = starter
        self.finder = finder
        self.processor = processor

    def start(self, image_url: str) -> PuzzleImport:
        return self.starter.start(image_url)

    def find_by_id(self, import_id: UUID) -> PuzzleImport:
        return self.finder.find_by_id(import_id)

    def process(self, import_id: UUID) -> None:
        self.processor.process(import_id)
