from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .clue_response import ClueResponse
from .grid_response import GridResponse


class PuzzleResponse(BaseModel):
    id: UUID
    name: str
    format: str
    hash: str
    clues: list[ClueResponse]
    grid: GridResponse
    created_at: datetime = Field(alias="createdAt")
