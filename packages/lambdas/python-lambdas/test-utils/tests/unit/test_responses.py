import pytest
from aws_lambda_typing.responses import APIGatewayProxyResponseV2

from crossword_solver_test_utils.responses import response_body, response_headers, response_json, response_status

RESPONSE: APIGatewayProxyResponseV2 = {
    "statusCode": 202,
    "headers": {"content-type": "application/json"},
    "body": '{"message": "ok"}',
}


def test_returns_response_parts():
    assert response_status(RESPONSE) == 202
    assert response_headers(RESPONSE) == {"content-type": "application/json"}
    assert response_body(RESPONSE) == '{"message": "ok"}'
    assert response_json(RESPONSE) == {"message": "ok"}


@pytest.mark.parametrize("function", [response_status, response_headers, response_body, response_json])
def test_raises_assertion_error_when_part_is_missing(function):
    with pytest.raises(AssertionError):
        function({})
