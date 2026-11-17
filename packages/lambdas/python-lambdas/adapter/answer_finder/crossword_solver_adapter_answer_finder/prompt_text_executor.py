import logging
from typing import Any

from .bedrock_conversation_config import BedrockConversationConfig

logger = logging.getLogger(__name__)


class PromptTextExecutor:
    def __init__(self, client: Any, conversation_config: BedrockConversationConfig, model_id: str):
        self.client = client
        self.conversation_config = conversation_config
        self.model_id = model_id

    def execute(self, prompt_text: str) -> str:
        logger.debug("Executing Bedrock prompt: %s", prompt_text)
        response = self.client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt_text}]}],
            inferenceConfig={
                "temperature": self.conversation_config.temperature,
                "maxTokens": self.conversation_config.max_tokens,
            },
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        logger.debug("Bedrock response: %s", response_text)
        return response_text
