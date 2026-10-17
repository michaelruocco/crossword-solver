import base64
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


def no_content_response() -> APIGatewayProxyResponseV2:
    return {"statusCode": 204, "headers": {}, "body": ""}


def binary_response(status_code: int, body: bytes, content_type: str) -> APIGatewayProxyResponseV2:
    return {
        "statusCode": status_code,
        "headers": {"content-type": content_type},
        "body": base64.b64encode(body).decode("ascii"),
        "isBase64Encoded": True,
    }
