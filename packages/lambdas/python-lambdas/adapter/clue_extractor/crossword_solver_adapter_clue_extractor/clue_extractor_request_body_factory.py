from .clue_extractor_prompt import CLUE_EXTRACTOR_PROMPT
from .invoke_model_request_body_factory import InvokeModelRequestBodyFactory


class ClueExtractorRequestBodyFactory:
    def __init__(
        self,
        invoke_model_request_body_factory: InvokeModelRequestBodyFactory | None = None,
    ):
        self.invoke_model_request_body_factory = invoke_model_request_body_factory or InvokeModelRequestBodyFactory()

    def to_request_body(self, image_bytes: bytes) -> str:
        return self.invoke_model_request_body_factory.to_request_body(
            image_bytes,
            CLUE_EXTRACTOR_PROMPT,
        )
