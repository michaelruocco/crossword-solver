from pydantic import BaseModel, Field


class CandidateAnswerResponse(BaseModel):
    id: str
    value: str
    confidence_score: int = Field(alias="confidenceScore")
