import re

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id

from .answer_request import AnswerRequest
from .answer_response import AnswerResponse

_ANSWER_ID_PATTERN = re.compile(r"([1-9][0-9]*)([AD])")


class AnswerConverter:
    def to_domain(self, request: AnswerRequest) -> Answer:
        match = _ANSWER_ID_PATTERN.fullmatch(request.id)
        if match is None:
            raise ValueError("Answer id must be a clue id such as 1A or 1D")

        return Answer(
            id=Id(number=int(match.group(1)), direction=Direction(match.group(2))),
            value=request.value,
        )

    def to_response(self, answer: Answer) -> AnswerResponse:
        return AnswerResponse(id=str(answer.id), value=answer.value)
