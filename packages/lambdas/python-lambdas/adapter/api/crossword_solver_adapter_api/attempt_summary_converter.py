from crossword_solver_domain_entities.attempt import Attempt

from .attempt_summary_response import AttemptSummaryResponse


class AttemptSummaryConverter:
    def to_response(self, attempt: Attempt) -> AttemptSummaryResponse:
        return AttemptSummaryResponse(
            id=attempt.id,
            createdAt=attempt.created_at,
            solving=attempt.solving,
            answerCount=attempt.answer_count,
            clueCount=len(attempt.puzzle.clues),
        )
