from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from .puzzle_repository import PuzzleRepository
from .puzzle_summary_page import PuzzleSummaryPage


class PuzzleSummaryLister:
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def __init__(self, repository: PuzzleRepository):
        self.repository = repository

    def list_page(self, limit: int = DEFAULT_PAGE_SIZE, cursor: str | None = None) -> PuzzleSummaryPage:
        if not 1 <= limit <= self.MAX_PAGE_SIZE:
            raise ValueError(f"limit must be between 1 and {self.MAX_PAGE_SIZE}")

        puzzles, next_cursor = self.repository.find_page(limit, cursor)
        return PuzzleSummaryPage([PuzzleSummary.from_puzzle(puzzle) for puzzle in puzzles], next_cursor)
