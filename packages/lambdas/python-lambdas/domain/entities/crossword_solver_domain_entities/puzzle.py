from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from crossword_solver_domain_entities.clues import Clues


@dataclass
class Puzzle:
    id: UUID
    name: str
    format: str
    hash: str
    clues: Clues
    created_at: datetime
