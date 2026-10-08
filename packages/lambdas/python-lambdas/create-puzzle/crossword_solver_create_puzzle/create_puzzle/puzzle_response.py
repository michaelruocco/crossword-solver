from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .clue_response import ClueResponse


class PuzzleResponse(BaseModel):
    id: UUID
    name: str
    format: str
    hash: str
    clues: list[ClueResponse]
    created_at: datetime = Field(alias="createdAt")
