import uuid as uid
from collections.abc import Callable
from uuid import UUID

from crossword_solver_domain_entities.attempt import Attempt

from .attempt_repository import AttemptRepository
from .clock import Clock, system_clock
from .puzzle_finder import PuzzleFinder


class AttemptCreator:
    def __init__(
        self,
        puzzle_finder: PuzzleFinder,
        repository: AttemptRepository,
        id_supplier: Callable[[], UUID] = uid.uuid4,
        clock: Clock = system_clock,
    ):
        self.puzzle_finder = puzzle_finder
        self.repository = repository
        self.id_supplier = id_supplier
        self.clock = clock

    def create(self, puzzle_id: UUID) -> UUID:
        attempt = Attempt(
            id=self.id_supplier(),
            created_at=self.clock(),
            puzzle=self.puzzle_finder.find_by_id(puzzle_id),
        )
        self.repository.save(attempt)
        return attempt.id
