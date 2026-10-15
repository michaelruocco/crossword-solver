from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .puzzle_import_status import PuzzleImportStatus


@dataclass
class PuzzleImport:
    id: UUID
    image_url: str
    status: PuzzleImportStatus
    created_at: datetime
    updated_at: datetime
    puzzle_id: UUID | None = None
    error: str | None = None
