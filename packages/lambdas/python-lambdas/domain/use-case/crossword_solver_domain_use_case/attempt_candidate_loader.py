from uuid import UUID

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id

from .attempt_finder import AttemptFinder
from .candidate_loader import CandidateLoader


class AttemptCandidateLoader:
    def __init__(self, attempt_finder: AttemptFinder, candidate_loader: CandidateLoader):
        self.attempt_finder = attempt_finder
        self.candidate_loader = candidate_loader

    def load_candidates(self, puzzle_id: UUID, attempt_id: UUID, clue_id: Id) -> Candidates:
        attempt = self.attempt_finder.find_by_id(puzzle_id, attempt_id)
        clue = attempt.puzzle.clues.find(clue_id)
        if clue is None:
            raise ClueNotFoundForIdError(clue_id)
        return self.candidate_loader.load_candidates(clue)
