import json

import boto3
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_use_case.clue_extractor import ClueExtractor
from crossword_solver_domain_use_case.image import Image
from crossword_solver_image.image_compressor import ImageCompressor

from .bedrock_clue import BedrockClue
from .bedrock_response import BedrockResponse
from .clue_extractor_request_body_factory import (
    ClueExtractorRequestBodyFactory,
)


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
        image_bytes = self.compressor.compress_and_resize(image.image)

        request_body = self.request_body_factory.to_request_body(image_bytes)

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=request_body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = response["body"].read().decode("utf-8")

        bedrock_response = BedrockResponse.model_validate_json(response_body)

        clues_json = bedrock_response.content[0].text

        bedrock_clues = json.loads(clues_json)

        clues = [BedrockClue.model_validate(clue).to_clue() for clue in bedrock_clues]

        return Clues(clues)
