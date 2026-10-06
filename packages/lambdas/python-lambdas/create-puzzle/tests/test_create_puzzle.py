import importlib
import json
import uuid

create_puzzle = importlib.import_module("crossword_solver_create_puzzle.create-puzzle.create_puzzle")


def build_event() -> dict:
    return {
        "version": "2.0",
        "routeKey": "POST /v1/puzzles",
        "rawPath": "/v1/puzzles",
        "rawQueryString": "",
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "domainName": "api-id.execute-api.eu-west-2.amazonaws.com",
            "domainPrefix": "api-id",
            "http": {
                "method": "POST",
                "path": "/v1/puzzles",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "agent",
            },
            "requestId": "request-id",
            "routeKey": "POST /v1/puzzles",
            "stage": "$default",
            "time": "01/Jan/2024:00:00:00 +0000",
            "timeEpoch": 1704067200000,
        },
        "isBase64Encoded": False,
    }


def test_handler_returns_created_puzzle_id(lambda_context):
    response = create_puzzle.lambda_handler(build_event(), lambda_context)

    assert response["statusCode"] == 201
    assert response["headers"]["content-type"] == "application/json"

    body = json.loads(response["body"])
    assert set(body) == {"id"}
    assert uuid.UUID(body["id"])
