import json

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model, SqsModel


def test_build_event_creates_valid_api_gateway_event(build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event({"imageUrl": "https://example.com/p.jpg"}))

    assert isinstance(event.body, str)
    assert json.loads(event.body) == {"imageUrl": "https://example.com/p.jpg"}
    assert event.pathParameters is None


def test_build_event_without_body_has_no_body(build_event):
    assert APIGatewayProxyEventV2Model.model_validate(build_event(None)).body is None


def test_build_event_includes_path_parameters(build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, {"id": "123"}))

    assert event.pathParameters == {"id": "123"}


def test_build_sqs_event_creates_a_record_per_body(build_sqs_event):
    event = SqsModel.model_validate(build_sqs_event("first", "second"))

    assert [record.body for record in event.Records] == ["first", "second"]


def test_lambda_context_provides_lambda_details(lambda_context):
    assert lambda_context.function_name == "test-function"
    assert lambda_context.memory_limit_in_mb == 512
    assert lambda_context.invoked_function_arn.endswith(":function:test-function")
    assert lambda_context.aws_request_id == "request-id"
