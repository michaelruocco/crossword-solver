from crossword_solver_domain_entities.puzzle import Puzzle

from .clue_response import ClueResponse
from .grid_response import GridResponse
from .puzzle_response import PuzzleResponse


class PuzzleConverter:
    def to_response(self, puzzle: Puzzle) -> PuzzleResponse:
        return PuzzleResponse(
            id=puzzle.id,
            name=puzzle.name,
            format=puzzle.format,
            hash=puzzle.hash,
            clues=[ClueResponse.from_clue(clue) for clue in puzzle.clues],
            grid=GridResponse.from_grid(puzzle.grid),
            createdAt=puzzle.created_at,
        )
