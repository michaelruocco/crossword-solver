from uuid import UUID

from crossword_solver_domain_entities.attempt import Attempt

from .attempt_repository import AttemptRepository
from .puzzle_finder import PuzzleFinder


class AttemptLister:
    def __init__(self, puzzle_finder: PuzzleFinder, repository: AttemptRepository):
        self.puzzle_finder = puzzle_finder
        self.repository = repository

    def list_by_puzzle_id(self, puzzle_id: UUID) -> list[Attempt]:
        puzzle = self.puzzle_finder.find_by_id(puzzle_id)
        return self.repository.find_by_puzzle(puzzle)
