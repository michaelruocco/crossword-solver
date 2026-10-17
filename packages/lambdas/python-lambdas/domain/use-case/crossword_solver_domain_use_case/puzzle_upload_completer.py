import logging
from uuid import UUID

from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .clock import Clock, system_clock
from .log_sanitizer import sanitize_for_log
from .puzzle_import_not_found_error import PuzzleImportNotFoundError
from .puzzle_import_queue import PuzzleImportQueue
from .puzzle_import_repository import PuzzleImportRepository

logger = logging.getLogger(__name__)


class PuzzleUploadCompleter:
    def __init__(self, repository: PuzzleImportRepository, queue: PuzzleImportQueue, clock: Clock = system_clock):
        self.repository = repository
        self.queue = queue
        self.clock = clock

    def complete(self, import_id: UUID) -> None:
        puzzle_import = self.repository.find_by_id(import_id)
        if puzzle_import is None:
            raise PuzzleImportNotFoundError(import_id)
        # Upload notifications can be delivered more than once, and a file can be uploaded again.
        if puzzle_import.status != PuzzleImportStatus.AWAITING_UPLOAD:
            logger.info(
                "Skipping upload for puzzle import %s as its status is %s",
                sanitize_for_log(import_id),
                puzzle_import.status.value,
            )
            return

        puzzle_import.upload_received(self.clock())
        self.repository.save(puzzle_import)
        self.queue.send(puzzle_import.id)
