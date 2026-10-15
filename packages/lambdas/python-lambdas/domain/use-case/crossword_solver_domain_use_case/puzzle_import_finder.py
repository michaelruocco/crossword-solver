from uuid import UUID

from crossword_solver_domain_entities.puzzle_import import PuzzleImport

from .puzzle_import_not_found_error import PuzzleImportNotFoundError
from .puzzle_import_repository import PuzzleImportRepository


class PuzzleImportFinder:
    def __init__(self, repository: PuzzleImportRepository):
        self.repository = repository

    def find_by_id(self, import_id: UUID) -> PuzzleImport:
        puzzle_import = self.repository.find_by_id(import_id)
        if puzzle_import is None:
            raise PuzzleImportNotFoundError(import_id)
        return puzzle_import
