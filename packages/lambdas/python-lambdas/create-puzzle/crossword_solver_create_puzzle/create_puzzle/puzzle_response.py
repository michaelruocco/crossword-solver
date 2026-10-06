from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PuzzleResponse(BaseModel):
    id: UUID
    name: str
    format: str
    hash: str
    created_at: datetime = Field(alias="createdAt")