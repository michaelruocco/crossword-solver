import json
from io import BytesIO

import boto3
import pytest
from botocore.config import Config
from botocore.exceptions import ClientError
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.clue_extractor_error import ClueExtractorError
from crossword_solver_domain_use_case.image import Image
from PIL import Image as PILImage
from pytest_httpserver import HTTPServer

from crossword_solver_adapter_clue_extractor.bedrock_clue_extractor import (
    BedrockClueExtractor,
)

MODEL_ID = BedrockClueExtractor.DEFAULT_MODEL_ID
INVOKE_PATH = f"/model/{MODEL_ID}/invoke"


@pytest.fixture
def extractor(httpserver: HTTPServer) -> BedrockClueExtractor:
    client = boto3.client(
        "bedrock-runtime",
        endpoint_url=httpserver.url_for(""),
        region_name="eu-west-2",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 1}),
    )
    return BedrockClueExtractor(client=client)


@pytest.fixture
def image() -> Image:
    pil_image = PILImage.new("RGB", (10, 10), "white")
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")
    return Image(name="puzzle", format=".jpg", pil_image=pil_image, bytes=buffer.getvalue(), hash="hash")


def bedrock_response(text: str) -> dict:
    return {
        "id": "msg_bdrk_01",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-4-6",
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 1500, "output_tokens": 120},
    }


def test_extract_clues(extractor, httpserver: HTTPServer, image):
    clues_json = json.dumps(
        [
            {"id": 1, "text": "Pacific republic (4)", "direction": "ACROSS", "lengths": [4]},
            {"id": 2, "text": "Stale (3,3)", "direction": "DOWN", "lengths": [3, 3]},
        ]
    )
    httpserver.expect_request(INVOKE_PATH, method="POST").respond_with_json(bedrock_response(clues_json))

    clues = extractor.extract_clues(image)

    assert len(clues) == 2
    across = clues.find(Id.across(1))
    assert across is not None
    assert across.text == "Pacific republic (4)"
    assert across.lengths == [4]
    down = clues.find(Id.down(2))
    assert down is not None
    assert down.text == "Stale (3,3)"
    assert down.lengths == [3, 3]


def test_extract_clues_sends_image_to_model(extractor, httpserver: HTTPServer, image):
    httpserver.expect_request(INVOKE_PATH, method="POST").respond_with_json(bedrock_response("[]"))

    extractor.extract_clues(image)

    request, _ = httpserver.log[0]
    assert request.headers["Content-Type"] == "application/json"
    body = request.get_json()
    assert body["anthropic_version"] == "bedrock-2023-05-31"
    content_types = [content["type"] for content in body["messages"][0]["content"]]
    assert content_types == ["text", "image"]


def test_extract_clues_raises_bedrock_error(extractor, httpserver: HTTPServer, image):
    httpserver.expect_request(INVOKE_PATH, method="POST").respond_with_json(
        {"message": "The provided model identifier is invalid."},
        status=400,
        headers={"x-amzn-ErrorType": "ValidationException"},
    )

    with pytest.raises(ClueExtractorError, match=f"Failed to invoke model {MODEL_ID}") as error:
        extractor.extract_clues(image)

    assert isinstance(error.value.__cause__, ClientError)


@pytest.mark.parametrize(
    "response",
    [
        bedrock_response("I could not find any clues in this image."),
        bedrock_response('[{"id": 1, "text": "Clue (4)", "direction": "SIDEWAYS", "lengths": [4]}]'),
        {**bedrock_response("[]"), "content": []},
    ],
    ids=["not json", "invalid clue", "no content"],
)
def test_extract_clues_raises_error_for_unparseable_response(extractor, httpserver: HTTPServer, image, response):
    httpserver.expect_request(INVOKE_PATH, method="POST").respond_with_json(response)

    with pytest.raises(ClueExtractorError, match="Failed to parse clues from model response"):
        extractor.extract_clues(image)
