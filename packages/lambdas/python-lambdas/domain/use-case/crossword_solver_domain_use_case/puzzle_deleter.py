from uuid import UUID

from .puzzle_repository import PuzzleRepository


class PuzzleDeleter:
    def __init__(self, repository: PuzzleRepository):
        self.repository = repository

    def delete(self, puzzle_id: UUID) -> None:
        self.repository.delete_by_id(puzzle_id)
