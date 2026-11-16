from typing import Protocol

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue


class AnswerFinder(Protocol):
    def find_candidates(self, clue: Clue, number_of_candidates: int) -> Candidates: ...
