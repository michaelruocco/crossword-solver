from crossword_solver_domain_entities.puzzle_import import PuzzleImport

from .image_fetcher import ImageFetcher
from .image_store import ImageStore
from .image_validator import ImageValidator
from .puzzle_import_starter import PuzzleImportStarter


class PuzzleUrlImportStarter:
    def __init__(
        self,
        fetcher: ImageFetcher,
        store: ImageStore,
        starter: PuzzleImportStarter,
        validator: ImageValidator | None = None,
    ):
        self.fetcher = fetcher
        self.store = store
        self.starter = starter
        self.validator = validator or ImageValidator()

    def start(self, source_url: str) -> PuzzleImport:
        file = self.fetcher.fetch(source_url, self.validator.max_size_in_bytes)
        self.validator.validate_file(file)
        return self.starter.start(self.store.save(file), source_url=source_url)
