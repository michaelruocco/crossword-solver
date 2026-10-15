from uuid import UUID

from .log_sanitizer import sanitize_for_log


class PuzzleImportNotFoundError(Exception):
    def __init__(self, import_id: UUID):
        super().__init__(f"Puzzle import not found with id {sanitize_for_log(import_id)}")
        self.import_id = import_id
