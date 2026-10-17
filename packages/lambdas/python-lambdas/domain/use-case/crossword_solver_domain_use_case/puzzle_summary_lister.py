from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from .puzzle_repository import PuzzleRepository


class PuzzleSummaryLister:
    def __init__(self, repository: PuzzleRepository):
        self.repository = repository

    def list_all(self) -> list[PuzzleSummary]:
        return [PuzzleSummary.from_puzzle(puzzle) for puzzle in self.repository.find_all()]
