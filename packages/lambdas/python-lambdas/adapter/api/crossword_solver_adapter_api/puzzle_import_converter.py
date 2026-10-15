from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .puzzle_import_response import PuzzleImportResponse

FAILED_MESSAGE = "Failed to import puzzle"


class PuzzleImportConverter:
    def to_response(self, puzzle_import: PuzzleImport) -> PuzzleImportResponse:
        return PuzzleImportResponse(
            id=puzzle_import.id,
            status=puzzle_import.status.value,
            puzzleId=puzzle_import.puzzle_id,
            puzzleUri=f"/v1/puzzles/{puzzle_import.puzzle_id}" if puzzle_import.puzzle_id else None,
            # The stored error can contain internal details, so clients get a generic message.
            error=FAILED_MESSAGE if puzzle_import.status == PuzzleImportStatus.FAILED else None,
            createdAt=puzzle_import.created_at,
            updatedAt=puzzle_import.updated_at,
        )

    def to_location(self, puzzle_import: PuzzleImport) -> str:
        return f"/v1/puzzles/imports/{puzzle_import.id}"
