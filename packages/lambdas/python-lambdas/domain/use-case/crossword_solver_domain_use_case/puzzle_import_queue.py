from typing import Protocol
from uuid import UUID


class PuzzleImportQueue(Protocol):
    def send(self, import_id: UUID) -> None: ...
