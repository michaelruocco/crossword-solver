import json

from aws_lambda_typing.responses import APIGatewayProxyResponseV2


def json_response(status_code: int, body: str, headers: dict[str, str] | None = None) -> APIGatewayProxyResponseV2:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json", **(headers or {})},
        "body": body,
    }


def message_response(status_code: int, message: str) -> APIGatewayProxyResponseV2:
    return json_response(status_code, json.dumps({"message": message}))
