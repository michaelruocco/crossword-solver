import json
import logging
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_use_case.clue_extractor import ClueExtractor
from crossword_solver_domain_use_case.clue_extractor_error import ClueExtractorError
from crossword_solver_domain_use_case.image import Image
from crossword_solver_image.image_compressor import ImageCompressor

from .bedrock_clue import BedrockClue
from .bedrock_response import BedrockResponse
from .clue_extractor_request_body_factory import (
    ClueExtractorRequestBodyFactory,
)

logger = logging.getLogger(__name__)


class BedrockClueExtractor(ClueExtractor):
    DEFAULT_MODEL_ID = "eu.anthropic.claude-opus-4-6-v1"

    def __init__(
        self,
        client=None,
        model_id: str | None = None,
        request_body_factory: ClueExtractorRequestBodyFactory | None = None,
        compressor: ImageCompressor | None = None,
    ):
        self.client = client or boto3.client("bedrock-runtime")
        self.model_id = model_id or self.DEFAULT_MODEL_ID
        self.request_body_factory = request_body_factory or ClueExtractorRequestBodyFactory()
        self.compressor = compressor or ImageCompressor()

    def extract_clues(self, image: Image) -> Clues:
        start = time.perf_counter()
        image_bytes = self.compressor.compress_and_resize(image.pil_image)
        compression_ms = _elapsed_ms(start)

        request_body = self.request_body_factory.to_request_body(image_bytes)

        invoke_start = time.perf_counter()
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=request_body,
                contentType="application/json",
                accept="application/json",
            )
            response_body = response["body"].read().decode("utf-8")
        except (BotoCoreError, ClientError) as e:
            raise ClueExtractorError(f"Failed to invoke model {self.model_id}") from e
        model_invocation_ms = _elapsed_ms(invoke_start)

        try:
            bedrock_response = BedrockResponse.model_validate_json(response_body)
            clues_json = bedrock_response.content[0].text
            bedrock_clues = json.loads(clues_json)
            clues = [BedrockClue.model_validate(clue).to_clue() for clue in bedrock_clues]
        except (ValueError, IndexError) as e:
            # pydantic ValidationError and JSONDecodeError are both ValueErrors
            raise ClueExtractorError("Failed to parse clues from model response") from e

        duration_ms = _elapsed_ms(start)
        logger.info(
            "Extracted %d clues in %d ms (compression %d ms, model invocation %d ms)",
            len(clues),
            duration_ms,
            compression_ms,
            model_invocation_ms,
            extra={
                "clue_extraction_duration_ms": duration_ms,
                "clue_compression_duration_ms": compression_ms,
                "clue_model_invocation_duration_ms": model_invocation_ms,
            },
        )
        return Clues(clues)


def _elapsed_ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)
