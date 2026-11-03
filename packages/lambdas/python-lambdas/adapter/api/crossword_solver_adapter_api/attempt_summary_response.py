from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AttemptSummaryResponse(BaseModel):
    id: UUID
    created_at: datetime = Field(alias="createdAt")
    solving: bool
    answer_count: int = Field(alias="answerCount")
    clue_count: int = Field(alias="clueCount")
