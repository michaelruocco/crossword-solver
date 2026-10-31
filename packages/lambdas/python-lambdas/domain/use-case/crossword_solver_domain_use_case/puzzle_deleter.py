from uuid import UUID

from .attempt_repository import AttemptRepository
from .puzzle_repository import PuzzleRepository


class PuzzleDeleter:
    def __init__(self, repository: PuzzleRepository, attempt_repository: AttemptRepository):
        self.repository = repository
        self.attempt_repository = attempt_repository

    def delete(self, puzzle_id: UUID) -> None:
        self.repository.delete_by_id(puzzle_id)
        self.attempt_repository.delete_by_puzzle_id(puzzle_id)
