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
    # The URL the image was fetched from, which is empty for uploaded files.
    source_url: str | None = None

    def upload_received(self, now: datetime) -> None:
        self.status = PuzzleImportStatus.PENDING
        self.updated_at = now

    def complete(self, puzzle_id: UUID, now: datetime) -> None:
        self.status = PuzzleImportStatus.COMPLETE
        self.puzzle_id = puzzle_id
        self.updated_at = now

    def fail(self, error: str, now: datetime) -> None:
        self.status = PuzzleImportStatus.FAILED
        self.error = error
        self.updated_at = now
