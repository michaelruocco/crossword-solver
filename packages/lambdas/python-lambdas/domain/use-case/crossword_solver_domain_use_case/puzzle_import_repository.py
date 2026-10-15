from typing import Protocol
from uuid import UUID

from crossword_solver_domain_entities.puzzle_import import PuzzleImport


class PuzzleImportRepository(Protocol):
    def find_by_id(self, import_id: UUID) -> PuzzleImport | None: ...

    def save(self, puzzle_import: PuzzleImport) -> None: ...
