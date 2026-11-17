import logging

from crossword_solver_domain_entities.clue import Clue

logger = logging.getLogger(__name__)


class DefaultFindAnswerPromptTextFactory:
    def __init__(self, find_candidates_prompt_template: str):
        self.find_candidates_prompt_template = find_candidates_prompt_template

    def to_prompt_text(self, clue: Clue, number_of_candidates: int) -> str:
        prompt_text = (
            self.find_candidates_prompt_template.replace("%CLUE_ID%", str(clue.id))
            .replace("%CLUE%", clue.text)
            .replace("%PATTERN%", clue.pattern)
            .replace("%NUMBER_OF_CANDIDATES%", str(number_of_candidates))
        )
        logger.debug("Built find-candidates prompt: %s", prompt_text)
        return prompt_text
