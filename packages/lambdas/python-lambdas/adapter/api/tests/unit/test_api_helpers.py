import json
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from crossword_solver_adapter_api.api_response import (
    binary_response,
    json_response,
    message_response,
    no_content_response,
)
from crossword_solver_adapter_api.path_parameters import (
    answer_id_path_parameter,
    attempt_answer_path_ids,
    attempt_id_path_parameter,
    puzzle_id_path_parameter,
    uuid_path_parameter,
)


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


def test_no_content_response_returns_an_empty_204_response():
    assert no_content_response() == {"statusCode": 204, "headers": {}, "body": ""}


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


def test_puzzle_and_attempt_id_path_parameters_read_their_named_ids(build_event):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    event = APIGatewayProxyEventV2Model.model_validate(
        build_event(None, {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id)})
    )

    assert puzzle_id_path_parameter(event) == puzzle_id
    assert attempt_id_path_parameter(event) == attempt_id


def test_attempt_answer_path_ids_returns_puzzle_and_attempt_ids(build_event):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    event = APIGatewayProxyEventV2Model.model_validate(
        build_event(None, {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id)})
    )
    logger = Mock(spec=Logger)

    assert attempt_answer_path_ids(event, logger) == (puzzle_id, attempt_id)
    logger.error.assert_not_called()


@pytest.mark.parametrize(
    ("path_parameters", "error", "log_message"),
    [
        ({"puzzleId": "invalid", "attemptId": str(uuid4())}, "Invalid puzzle id", "Invalid puzzle id path parameter"),
        ({"attemptId": str(uuid4())}, "Invalid puzzle id", "Invalid puzzle id path parameter"),
        ({"puzzleId": str(uuid4()), "attemptId": "invalid"}, "Invalid attempt id", "Invalid attempt id path parameter"),
        ({"puzzleId": str(uuid4())}, "Invalid attempt id", "Invalid attempt id path parameter"),
    ],
)
def test_attempt_answer_path_ids_logs_and_raises_for_invalid_ids(build_event, path_parameters, error, log_message):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, path_parameters))
    logger = Mock(spec=Logger)

    with pytest.raises(ValueError, match=error):
        attempt_answer_path_ids(event, logger)

    logger.error.assert_called_once_with(log_message, exc_info=True)


def test_answer_id_path_parameter_reads_its_named_id(build_event):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, {"answerId": "23D"}))

    assert answer_id_path_parameter(event) == "23D"


@pytest.mark.parametrize("path_parameters", [None, {}, {"answerId": ""}])
def test_answer_id_path_parameter_raises_when_missing_or_empty(build_event, path_parameters):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, path_parameters))

    with pytest.raises(ValueError, match="answerId path parameter is required"):
        answer_id_path_parameter(event)


@pytest.mark.parametrize(
    ("path_parameter", "path_parameters", "error"),
    [
        (puzzle_id_path_parameter, {"puzzleId": "invalid"}, "puzzleId path parameter must be a valid UUID"),
        (attempt_id_path_parameter, {"attemptId": "invalid"}, "attemptId path parameter must be a valid UUID"),
        (puzzle_id_path_parameter, {}, "puzzleId path parameter is required"),
        (attempt_id_path_parameter, {}, "attemptId path parameter is required"),
    ],
)
def test_required_id_path_parameters_raise_for_invalid_or_missing_values(
    build_event, path_parameter, path_parameters, error
):
    event = APIGatewayProxyEventV2Model.model_validate(build_event(None, path_parameters))

    with pytest.raises(ValueError, match=error):
        path_parameter(event)
