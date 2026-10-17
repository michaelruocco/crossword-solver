from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PuzzleSummaryResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime = Field(alias="createdAt")
    clue_count: int = Field(alias="clueCount")


class PuzzleSummaryPageResponse(BaseModel):
    summaries: list[PuzzleSummaryResponse]
    next_cursor: str | None = Field(alias="nextCursor")
