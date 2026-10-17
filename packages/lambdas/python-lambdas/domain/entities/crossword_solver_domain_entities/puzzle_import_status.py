from enum import Enum


class PuzzleImportStatus(Enum):
    AWAITING_UPLOAD = "AWAITING_UPLOAD"
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
