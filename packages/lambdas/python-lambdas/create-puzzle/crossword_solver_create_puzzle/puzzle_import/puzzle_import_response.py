from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PuzzleImportResponse(BaseModel):
    id: UUID
    status: str
    puzzle_id: UUID | None = Field(default=None, alias="puzzleId")
    puzzle_uri: str | None = Field(default=None, alias="puzzleUri")
    error: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
