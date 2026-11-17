import logging

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue

from .answer_finder import AnswerFinder
from .candidate_repository import CandidateRepository

logger = logging.getLogger(__name__)


class CandidateLoader:
    def __init__(self, answer_finder: AnswerFinder, repository: CandidateRepository):
        self.answer_finder = answer_finder
        self.repository = repository

    def load_candidates(self, clue: Clue, candidates_per_clue: int = 5) -> Candidates:
        logger.debug("getting candidates for clue %s", clue.as_string())
        cached_candidates = self.repository.get(clue)
        if cached_candidates is not None:
            return cached_candidates

        logger.info("loading candidates from answer finder for clue %s", clue.as_string())
        candidates = self.answer_finder.find_candidates(clue, candidates_per_clue).valid_answers(clue)
        if not candidates.is_empty():
            self.repository.save(candidates)
        return candidates
