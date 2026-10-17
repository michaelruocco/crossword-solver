from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .puzzle import Puzzle


@dataclass(frozen=True)
class PuzzleSummary:
    id: UUID
    name: str
    created_at: datetime
    clue_count: int

    @classmethod
    def from_puzzle(cls, puzzle: Puzzle) -> PuzzleSummary:
        return cls(
            id=puzzle.id,
            name=puzzle.name,
            created_at=puzzle.created_at,
            clue_count=len(puzzle.clues),
        )
