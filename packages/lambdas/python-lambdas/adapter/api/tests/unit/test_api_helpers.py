import json
from uuid import UUID, uuid4

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from crossword_solver_adapter_api.api_response import binary_response, json_response, message_response
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter


def test_json_response_adds_content_type_and_extra_headers():
    assert json_response(202, "{}", {"location": "/somewhere"}) == {
        "statusCode": 202,
        "headers": {"content-type": "application/json", "location": "/somewhere"},
        "body": "{}",
    }


def test_message_response_wraps_message_in_json():
    assert message_response(404, "Not found") == {
        "statusCode": 404,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"message": "Not found"}),
    }


def test_binary_response_base64_encodes_body_and_sets_content_type():
    assert binary_response(200, b"binary", "image/png") == {
        "statusCode": 200,
        "headers": {"content-type": "image/png"},
        "body": "YmluYXJ5",
        "isBase64Encoded": True,
    }


def test_uuid_path_parameter_returns_uuid(build_event):
    value = uuid4()
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, {"id": str(value)}))

    assert uuid_path_parameter(event, "id") == value
    assert isinstance(uuid_path_parameter(event, "id"), UUID)


def test_uuid_path_parameter_returns_none_when_invalid_or_missing(build_event):
    invalid = APIGatewayProxyEventV2Model.model_validate(build_event(None, {"id": "nope"}))
    missing = APIGatewayProxyEventV2Model.model_validate(build_event(None))

    assert uuid_path_parameter(invalid, "id") is None
    assert uuid_path_parameter(missing, "id") is None
