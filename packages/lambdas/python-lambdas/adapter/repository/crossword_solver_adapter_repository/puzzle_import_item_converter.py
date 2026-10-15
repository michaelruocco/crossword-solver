from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

Item = dict[str, Any]


class PuzzleImportItemConverter:
    DEFAULT_TTL = timedelta(days=7)

    def __init__(self, ttl: timedelta = DEFAULT_TTL):
        self.ttl = ttl

    def to_item(self, puzzle_import: PuzzleImport) -> Item:
        return {
            "id": str(puzzle_import.id),
            "image_url": puzzle_import.image_url,
            "status": puzzle_import.status.value,
            "puzzle_id": str(puzzle_import.puzzle_id) if puzzle_import.puzzle_id else None,
            "error": puzzle_import.error,
            "created_at": puzzle_import.created_at.isoformat(),
            "updated_at": puzzle_import.updated_at.isoformat(),
            # Epoch seconds, which the table's TTL setting reads to expire the item.
            "expires_at": int((puzzle_import.created_at + self.ttl).timestamp()),
        }

    def to_puzzle_import(self, item: Item) -> PuzzleImport:
        return PuzzleImport(
            id=UUID(item["id"]),
            image_url=item["image_url"],
            status=PuzzleImportStatus(item["status"]),
            puzzle_id=UUID(item["puzzle_id"]) if item.get("puzzle_id") else None,
            error=item.get("error"),
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )
