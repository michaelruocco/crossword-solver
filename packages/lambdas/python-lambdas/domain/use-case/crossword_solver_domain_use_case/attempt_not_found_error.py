from uuid import UUID


class AttemptNotFoundError(Exception):
    def __init__(self, puzzle_id: UUID, attempt_id: UUID):
        super().__init__(f"Attempt {attempt_id} not found for puzzle {puzzle_id}")
        self.puzzle_id = puzzle_id
        self.attempt_id = attempt_id
