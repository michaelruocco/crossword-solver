from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Puzzle:
    id: UUID
    name: str
    format: str
    hash: str
    created_at: datetime
