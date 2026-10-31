from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .puzzle import Puzzle


@dataclass
class Attempt:
    id: UUID
    created_at: datetime
    puzzle: Puzzle
    solving: bool = False
    answer_count: int = 0

    @property
    def puzzle_id(self) -> UUID:
        return self.puzzle.id
