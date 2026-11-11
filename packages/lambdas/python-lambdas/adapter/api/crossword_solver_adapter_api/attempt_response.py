from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .answer_response import AnswerResponse
from .puzzle_response import PuzzleResponse


class AttemptResponse(BaseModel):
    id: UUID
    created_at: datetime = Field(alias="createdAt")
    solving: bool
    puzzle: PuzzleResponse
    answer_count: int = Field(alias="answerCount")
    answers: list[AnswerResponse] = Field(default_factory=list)
