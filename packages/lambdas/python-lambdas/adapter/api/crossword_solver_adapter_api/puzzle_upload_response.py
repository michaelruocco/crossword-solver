from pydantic import BaseModel

from .puzzle_import_response import PuzzleImportResponse


class UploadResponse(BaseModel):
    url: str
    fields: dict[str, str]


class PuzzleUploadResponse(PuzzleImportResponse):
    upload: UploadResponse
