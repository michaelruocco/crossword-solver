from typing import Protocol

from crossword_solver_domain_entities.clue import Clue


class FindAnswerPromptTextFactory(Protocol):
    def to_prompt_text(self, clue: Clue, number_of_candidates: int) -> str: ...
