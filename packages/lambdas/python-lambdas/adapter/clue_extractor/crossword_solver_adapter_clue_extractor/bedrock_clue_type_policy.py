import logging
from typing import Any

import boto3
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_use_case.clue_type_policy import ClueTypePolicy

from .bedrock_conversation_config import BedrockConversationConfig
from .determine_puzzle_type_prompt_text_factory import DeterminePuzzleTypePromptTextFactory

logger = logging.getLogger(__name__)


class BedrockClueTypePolicy(ClueTypePolicy):
    DEFAULT_MODEL_ID = "eu.anthropic.claude-opus-4-6-v1"

    def __init__(
        self,
        client: Any | None = None,
        conversation_config: BedrockConversationConfig | None = None,
        model_id: str | None = None,
        prompt_text_factory: DeterminePuzzleTypePromptTextFactory | None = None,
    ):
        self.client = client if client is not None else boto3.client("bedrock-runtime")
        self.conversation_config = conversation_config or BedrockConversationConfig()
        self.model_id = model_id or self.DEFAULT_MODEL_ID
        self.prompt_text_factory = prompt_text_factory or DeterminePuzzleTypePromptTextFactory()

    def determine_clue_type(self, clues: Clues) -> ClueType:
        prompt_text = self.prompt_text_factory.to_prompt_text(clues)
        response = self.client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt_text}]}],
            inferenceConfig={
                "temperature": self.conversation_config.temperature,
                "maxTokens": self.conversation_config.max_tokens,
            },
        )
        response_text = response["output"]["message"]["content"][0]["text"].strip()
        logger.debug("Determined clue type: %s", response_text)
        return ClueType(response_text)
