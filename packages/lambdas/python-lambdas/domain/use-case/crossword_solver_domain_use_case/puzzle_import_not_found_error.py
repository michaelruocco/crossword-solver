from uuid import UUID


class PuzzleImportNotFoundError(Exception):
    def __init__(self, import_id: UUID):
        super().__init__(f"Puzzle import not found with id {import_id}")
        self.import_id = import_id
