from uuid import UUID

from crossword_solver_domain_entities.puzzle import Puzzle

from .puzzle_creator import PuzzleCreator
from .puzzle_finder import PuzzleFinder


class PuzzleService:
    def __init__(self, creator: PuzzleCreator, finder: PuzzleFinder):
        self.creator = creator
        self.finder = finder

    def create(self, image_url: str) -> UUID:
        return self.creator.create(image_url)

    def find_by_id(self, puzzle_id: UUID) -> Puzzle:
        return self.finder.find_by_id(puzzle_id)
