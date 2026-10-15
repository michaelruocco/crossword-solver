from enum import Enum


class PuzzleImportStatus(Enum):
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
