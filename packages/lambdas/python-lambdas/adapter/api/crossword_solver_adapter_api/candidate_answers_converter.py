from crossword_solver_domain_entities.candidates import Candidates

from .candidate_answer_response import CandidateAnswerResponse
from .candidate_answers_response import CandidateAnswersResponse
from .clue_response import ClueResponse


class CandidateAnswersConverter:
    def to_response(self, candidates: Candidates) -> CandidateAnswersResponse:
        answers = sorted(candidates, key=lambda answer: answer.confidence_score, reverse=True)
        return CandidateAnswersResponse(
            clue=ClueResponse.from_clue(candidates.clue),
            answers=[
                CandidateAnswerResponse(
                    id=str(answer.id),
                    value=answer.value,
                    confidenceScore=answer.confidence_score,
                )
                for answer in answers
            ],
        )
