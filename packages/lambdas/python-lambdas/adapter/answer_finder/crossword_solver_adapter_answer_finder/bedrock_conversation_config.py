from typing import Protocol


class BedrockConversationConfig(Protocol):
    @property
    def temperature(self) -> float: ...

    @property
    def max_tokens(self) -> int: ...


class DefaultBedrockConversationConfig:
    temperature = 0.0
    max_tokens = 2048
