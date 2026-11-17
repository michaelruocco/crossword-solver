from typing import Protocol

from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues


class ClueTypePolicy(Protocol):
    def determine_clue_type(self, clues: Clues) -> ClueType: ...
