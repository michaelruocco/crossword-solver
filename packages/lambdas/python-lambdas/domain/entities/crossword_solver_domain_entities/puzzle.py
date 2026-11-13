from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.intersection import Intersection
from crossword_solver_domain_entities.words import Words


@dataclass
class Puzzle:
    id: UUID
    name: str
    format: str
    hash: str
    clues: Clues
    grid: Grid
    words: Words
    created_at: datetime

    def intersections(self, clue_id: Id) -> list[Intersection]:
        return self.words.get_intersections_by_id(clue_id)
