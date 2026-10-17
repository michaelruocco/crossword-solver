import pytest
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from crossword_solver_adapter_api.api_gateway_event_converter import (
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


def test_to_upload_request(converter, build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event({"fileName": "puzzle14.png"}))

    request = converter.to_upload_request(event)

    assert request.file_name == "puzzle14.png"


@pytest.mark.parametrize("body", [None, {}, {"fileName": ""}, {"fileName": "a" * 256}])
def test_to_upload_request_rejects_invalid_requests(converter, build_event, body):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(body))

    with pytest.raises(ValueError):
        converter.to_upload_request(event)


def test_to_puzzle_summary_query_uses_defaults(converter, build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None))

    query = converter.to_puzzle_summary_query(event)

    assert query.limit == 20
    assert query.cursor is None


def test_to_puzzle_summary_query_reads_limit_and_cursor(converter, build_event):
    raw_event = build_event(None)
    raw_event["queryStringParameters"] = {"limit": "5", "cursor": "next-page"}
    event = APIGatewayProxyEventV2Model.model_validate(raw_event)

    query = converter.to_puzzle_summary_query(event)

    assert query.limit == 5
    assert query.cursor == "next-page"


@pytest.mark.parametrize("limit", ["0", "101", "not-a-number"])
def test_to_puzzle_summary_query_rejects_invalid_limits(converter, build_event, limit):
    raw_event = build_event(None)
    raw_event["queryStringParameters"] = {"limit": limit}
    event = APIGatewayProxyEventV2Model.model_validate(raw_event)

    with pytest.raises(ValueError):
        converter.to_puzzle_summary_query(event)
