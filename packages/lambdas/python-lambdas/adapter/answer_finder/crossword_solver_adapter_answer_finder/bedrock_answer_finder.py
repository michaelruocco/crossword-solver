from typing import Any

import boto3
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_use_case.answer_finder import AnswerFinder

from .bedrock_conversation_config import BedrockConversationConfig, DefaultBedrockConversationConfig
from .delegating_find_answer_prompt_text_factory import DelegatingFindAnswerPromptTextFactory
from .find_answer_prompt_text_factory import FindAnswerPromptTextFactory
from .find_answer_response_converter import FindAnswerResponseConverter
from .prompt_text_executor import PromptTextExecutor


class BedrockAnswerFinder(AnswerFinder):
    DEFAULT_MODEL_ID = "eu.anthropic.claude-opus-4-6-v1"

    def __init__(
        self,
        client: Any | None = None,
        conversation_config: BedrockConversationConfig | None = None,
        model_id: str | None = None,
        prompt_text_factory: FindAnswerPromptTextFactory | None = None,
        response_converter: FindAnswerResponseConverter | None = None,
        prompt_text_executor: PromptTextExecutor | None = None,
    ):
        if prompt_text_executor is None:
            bedrock_client = client if client is not None else boto3.client("bedrock-runtime")
            prompt_text_executor = PromptTextExecutor(
                bedrock_client,
                conversation_config or DefaultBedrockConversationConfig(),
                model_id or self.DEFAULT_MODEL_ID,
            )
        self.prompt_text_executor = prompt_text_executor
        self.prompt_text_factory = prompt_text_factory or DelegatingFindAnswerPromptTextFactory()
        self.response_converter = response_converter or FindAnswerResponseConverter()

    def find_candidates(self, clue: Clue, number_of_candidates: int) -> Candidates:
        prompt_text = self.prompt_text_factory.to_prompt_text(clue, number_of_candidates)
        response_text = self.prompt_text_executor.execute(prompt_text)
        answers = self.response_converter.to_candidates(response_text)
        return Candidates(clue, answers).valid_answers(clue)
