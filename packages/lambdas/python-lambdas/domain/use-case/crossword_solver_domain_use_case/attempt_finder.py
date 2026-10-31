from uuid import UUID

from crossword_solver_domain_entities.attempt import Attempt

from .attempt_not_found_error import AttemptNotFoundError
from .attempt_repository import AttemptRepository


class AttemptFinder:
    def __init__(self, repository: AttemptRepository):
        self.repository = repository

    def find_by_id(self, puzzle_id: UUID, attempt_id: UUID) -> Attempt:
        attempt = self.repository.find_by_id(puzzle_id, attempt_id)
        if attempt is None:
            raise AttemptNotFoundError(puzzle_id, attempt_id)
        return attempt
