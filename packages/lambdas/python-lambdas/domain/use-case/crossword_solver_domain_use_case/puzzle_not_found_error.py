from uuid import UUID


class PuzzleNotFoundError(Exception):
    def __init__(self, puzzle_id: UUID):
        super().__init__(f"Puzzle not found with id {puzzle_id}")
        self.puzzle_id = puzzle_id
