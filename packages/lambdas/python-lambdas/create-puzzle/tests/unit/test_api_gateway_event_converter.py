import pytest
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from crossword_solver_create_puzzle.create_puzzle.api_gateway_event_converter import (
    ApiGatewayEventConverter,
)


@pytest.fixture
def converter() -> ApiGatewayEventConverter:
    return ApiGatewayEventConverter()


def test_to_request(converter, build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event({"imageUrl": "https://example.com/puzzle14.jpg"}))

    request = converter.to_request(event)

    assert request.image_url == "https://example.com/puzzle14.jpg"


def test_to_request_raises_error_when_body_missing(converter, build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None))

    with pytest.raises(ValueError, match="Request body is missing"):
        converter.to_request(event)
