from uuid import UUID

from crossword_solver_domain_entities.puzzle import Puzzle

from .puzzle_not_found_error import PuzzleNotFoundError
from .puzzle_repository import PuzzleRepository


class PuzzleFinder:
    def __init__(self, repository: PuzzleRepository):
        self.repository = repository

    def find_by_id(self, puzzle_id: UUID) -> Puzzle:
        puzzle = self.repository.find_by_id(puzzle_id)
        if puzzle is None:
            raise PuzzleNotFoundError(puzzle_id)
        return puzzle
