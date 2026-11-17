from crossword_solver_domain_entities.clues import Clues

from .determine_puzzle_type_prompt import DETERMINE_PUZZLE_TYPE_PROMPT


class DeterminePuzzleTypePromptTextFactory:
    def to_prompt_text(self, clues: Clues) -> str:
        clues_text = "\n".join(f"{clue.id}|{clue.text}" for clue in clues)
        return DETERMINE_PUZZLE_TYPE_PROMPT.replace("%CLUES%", clues_text)
