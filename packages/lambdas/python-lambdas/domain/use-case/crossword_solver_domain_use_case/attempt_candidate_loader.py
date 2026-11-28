from uuid import UUID

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id

from .attempt_finder import AttemptFinder
from .candidate_loader import CandidateLoader
from .pattern_factory import PatternFactory


class AttemptCandidateLoader:
    def __init__(
        self,
        attempt_finder: AttemptFinder,
        candidate_loader: CandidateLoader,
        pattern_factory: PatternFactory | None = None,
    ):
        self.attempt_finder = attempt_finder
        self.candidate_loader = candidate_loader
        self.pattern_factory = pattern_factory or PatternFactory()

    def load_candidates(self, puzzle_id: UUID, attempt_id: UUID, clue_id: Id) -> Candidates:
        attempt = self.attempt_finder.find_by_id(puzzle_id, attempt_id)
        clues = self.pattern_factory.add_patterns_to_clues(attempt.puzzle.clues, attempt)
        clue = clues.find(clue_id)
        if clue is None:
            raise ClueNotFoundForIdError(clue_id)
        return self.candidate_loader.load_candidates(clue)
