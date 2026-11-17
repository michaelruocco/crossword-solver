from pydantic import BaseModel

from .candidate_answer_response import CandidateAnswerResponse
from .clue_response import ClueResponse


class CandidateAnswersResponse(BaseModel):
    clue: ClueResponse
    answers: list[CandidateAnswerResponse]
