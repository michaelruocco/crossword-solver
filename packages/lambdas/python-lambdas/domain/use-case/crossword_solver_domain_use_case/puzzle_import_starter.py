import uuid as uid

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .clock import Clock, system_clock
from .puzzle_import_queue import PuzzleImportQueue
from .puzzle_import_repository import PuzzleImportRepository


class PuzzleImportStarter:
    def __init__(self, repository: PuzzleImportRepository, queue: PuzzleImportQueue, clock: Clock = system_clock):
        self.repository = repository
        self.queue = queue
        self.clock = clock

    def start(self, image_url: str, source_url: str | None = None) -> PuzzleImport:
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
