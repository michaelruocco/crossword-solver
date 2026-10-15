import json
from typing import Any

from aws_lambda_typing.responses import APIGatewayProxyResponseV2


def response_status(response: APIGatewayProxyResponseV2) -> int:
    status = response.get("statusCode")
    assert status is not None, "response has no statusCode"
    return status


def response_headers(response: APIGatewayProxyResponseV2) -> dict[str, str]:
    headers = response.get("headers")
    assert headers is not None, "response has no headers"
    return headers


def response_body(response: APIGatewayProxyResponseV2) -> str:
    body = response.get("body")
    assert body is not None, "response has no body"
    return body


def response_json(response: APIGatewayProxyResponseV2) -> Any:
    return json.loads(response_body(response))
