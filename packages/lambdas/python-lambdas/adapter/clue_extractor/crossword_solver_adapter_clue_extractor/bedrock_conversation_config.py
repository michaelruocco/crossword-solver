from dataclasses import dataclass


@dataclass(frozen=True)
class BedrockConversationConfig:
    temperature: float = 0.0
    max_tokens: int = 2048
