import logging

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType

from .default_find_answer_prompt_text_factory import DefaultFindAnswerPromptTextFactory
from .find_answer_prompt_text_factory import FindAnswerPromptTextFactory
from .find_answer_prompts import CRYPTIC_FIND_ANSWER_PROMPT, STANDARD_FIND_ANSWER_PROMPT

logger = logging.getLogger(__name__)


class DelegatingFindAnswerPromptTextFactory:
    def __init__(
        self,
        standard_factory: FindAnswerPromptTextFactory | None = None,
        cryptic_factory: FindAnswerPromptTextFactory | None = None,
    ):
        self.standard_factory = standard_factory or self.build(ClueType.STANDARD)
        self.cryptic_factory = cryptic_factory or self.build(ClueType.CRYPTIC)

    def to_prompt_text(self, clue: Clue, number_of_candidates: int) -> str:
        clue_type = clue.type or ClueType.STANDARD
        logger.debug("Selecting %s find-answer prompt factory", clue_type)
        factory = self.cryptic_factory if clue_type == ClueType.CRYPTIC else self.standard_factory
        return factory.to_prompt_text(clue, number_of_candidates)

    @staticmethod
    def build(clue_type: ClueType) -> FindAnswerPromptTextFactory:
        prompt = CRYPTIC_FIND_ANSWER_PROMPT if clue_type == ClueType.CRYPTIC else STANDARD_FIND_ANSWER_PROMPT
        return DefaultFindAnswerPromptTextFactory(prompt)
