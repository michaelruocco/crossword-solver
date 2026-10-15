from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid
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
