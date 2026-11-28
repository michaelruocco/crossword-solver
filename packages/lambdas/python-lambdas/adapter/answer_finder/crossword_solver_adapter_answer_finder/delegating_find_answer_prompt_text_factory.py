import logging

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType

from .default_find_answer_prompt_text_factory import DefaultFindAnswerPromptTextFactory
from .find_answer_prompt_text_factory import FindAnswerPromptTextFactory
from .find_answer_prompts import CRYPTIC_FIND_ANSWER_PROMPT, MATH_FIND_ANSWER_PROMPT, STANDARD_FIND_ANSWER_PROMPT

logger = logging.getLogger(__name__)


class DelegatingFindAnswerPromptTextFactory:
    def __init__(
        self,
        standard_factory: FindAnswerPromptTextFactory | None = None,
        cryptic_factory: FindAnswerPromptTextFactory | None = None,
        math_factory: FindAnswerPromptTextFactory | None = None,
    ):
        self.standard_factory = standard_factory or self.build(ClueType.STANDARD)
        self.cryptic_factory = cryptic_factory or self.build(ClueType.CRYPTIC)
        self.math_factory = math_factory or self.build(ClueType.MATH)

    def to_prompt_text(self, clue: Clue, number_of_candidates: int) -> str:
        clue_type = clue.type or ClueType.STANDARD
        logger.debug("Selecting %s find-answer prompt factory", clue_type)
        if clue_type == ClueType.CRYPTIC:
            factory = self.cryptic_factory
        elif clue_type == ClueType.MATH:
            factory = self.math_factory
        else:
            factory = self.standard_factory
        return factory.to_prompt_text(clue, number_of_candidates)

    @staticmethod
    def build(clue_type: ClueType) -> FindAnswerPromptTextFactory:
        if clue_type == ClueType.CRYPTIC:
            prompt = CRYPTIC_FIND_ANSWER_PROMPT
        elif clue_type == ClueType.MATH:
            prompt = MATH_FIND_ANSWER_PROMPT
        else:
            prompt = STANDARD_FIND_ANSWER_PROMPT
        return DefaultFindAnswerPromptTextFactory(prompt)
