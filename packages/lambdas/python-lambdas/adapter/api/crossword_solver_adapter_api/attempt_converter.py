from crossword_solver_domain_entities.attempt import Attempt

from .answer_converter import AnswerConverter
from .attempt_response import AttemptResponse
from .puzzle_converter import PuzzleConverter


class AttemptConverter:
    def __init__(
        self,
        puzzle_converter: PuzzleConverter | None = None,
        answer_converter: AnswerConverter | None = None,
    ):
        self.puzzle_converter = puzzle_converter or PuzzleConverter()
        self.answer_converter = answer_converter or AnswerConverter()

    def to_response(self, attempt: Attempt) -> AttemptResponse:
        return AttemptResponse(
            id=attempt.id,
            createdAt=attempt.created_at,
            solving=attempt.solving,
            puzzle=self.puzzle_converter.to_response(attempt.puzzle),
            answerCount=attempt.answer_count,
            answers=[self.answer_converter.to_response(answer) for answer in attempt.answers],
        )
