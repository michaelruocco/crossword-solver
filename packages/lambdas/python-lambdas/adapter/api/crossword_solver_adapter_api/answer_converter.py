import re

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id

from .answer_request import AnswerRequest
from .answer_response import AnswerResponse

_ANSWER_ID_PATTERN = re.compile(r"([1-9]\d*)([AD])")


class AnswerConverter:
    def to_id(self, clue_id: str) -> Id:
        match = _ANSWER_ID_PATTERN.fullmatch(clue_id)
        if match is None:
            raise ValueError("Answer id must be a clue id such as 1A or 1D")

        return Id(number=int(match.group(1)), direction=Direction(match.group(2)))

    def to_answer(self, request: AnswerRequest) -> Answer:
        return Answer(id=self.to_id(request.id), value=request.value, confidence_score=100)

    def to_response(self, answer: Answer) -> AnswerResponse:
        return AnswerResponse(id=str(answer.id), value=answer.value)
