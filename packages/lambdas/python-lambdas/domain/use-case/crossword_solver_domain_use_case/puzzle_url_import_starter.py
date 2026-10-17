import uuid as uid

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .clock import Clock, system_clock
from .image_fetcher import ImageFetcher
from .image_store import ImageStore
from .image_validator import ImageValidator
from .puzzle_import_queue import PuzzleImportQueue
from .puzzle_import_repository import PuzzleImportRepository


class PuzzleUrlImportStarter:
    def __init__(
        self,
        fetcher: ImageFetcher,
        store: ImageStore,
        repository: PuzzleImportRepository,
        queue: PuzzleImportQueue,
        validator: ImageValidator | None = None,
        clock: Clock = system_clock,
    ):
        self.fetcher = fetcher
        self.store = store
        self.repository = repository
        self.queue = queue
        self.validator = validator or ImageValidator()
        self.clock = clock

    def start(self, source_url: str) -> PuzzleImport:
        file = self.fetcher.fetch(source_url, self.validator.max_size_in_bytes)
        self.validator.validate_file(file)
        image_url = self.store.save(file)
        now = self.clock()
        puzzle_import = PuzzleImport(
            id=uid.uuid4(),
            image_url=image_url,
            status=PuzzleImportStatus.PENDING,
            created_at=now,
            updated_at=now,
            source_url=source_url,
        )
        # Saved before queueing so the worker can always find the import it is sent.
        self.repository.save(puzzle_import)
        self.queue.send(puzzle_import.id)
        return puzzle_import
