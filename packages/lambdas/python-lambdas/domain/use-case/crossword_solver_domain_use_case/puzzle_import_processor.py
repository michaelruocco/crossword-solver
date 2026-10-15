import logging
from uuid import UUID

from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .clock import Clock, system_clock
from .puzzle_creator import PuzzleCreator
from .puzzle_import_not_found_error import PuzzleImportNotFoundError
from .puzzle_import_repository import PuzzleImportRepository

logger = logging.getLogger(__name__)


class PuzzleImportProcessor:
    def __init__(self, repository: PuzzleImportRepository, creator: PuzzleCreator, clock: Clock = system_clock):
        self.repository = repository
        self.creator = creator
        self.clock = clock

    def process(self, import_id: UUID) -> None:
        puzzle_import = self.repository.find_by_id(import_id)
        if puzzle_import is None:
            raise PuzzleImportNotFoundError(import_id)
        if puzzle_import.status != PuzzleImportStatus.PENDING:
            logger.info("Skipping puzzle import %s as its status is %s", import_id, puzzle_import.status.value)
            return

        try:
            puzzle_id = self.creator.create(puzzle_import.image_url)
        except Exception as e:
            # Recorded on the import for the client to see, rather than letting the queue retry an expensive call.
            logger.exception("Failed to process puzzle import %s", import_id)
            puzzle_import.fail(str(e) or type(e).__name__, self.clock())
        else:
            puzzle_import.complete(puzzle_id, self.clock())
        self.repository.save(puzzle_import)
