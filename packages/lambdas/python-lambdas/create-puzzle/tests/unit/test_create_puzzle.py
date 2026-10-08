import json
import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from crossword_solver_domain_entities.puzzle import Puzzle

from crossword_solver_create_puzzle.create_puzzle import create_puzzle


def build_event(body: dict) -> dict:
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
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }


def test_handler_returns_created_puzzle(lambda_context):
    puzzle = Puzzle(
        id=uuid.uuid4(),
        name="puzzle14",
        format=".jpg",
        hash="hash-value",
        created_at=datetime.now(UTC),
    )

    image_url = "https://example.com/puzzle14.jpg"
    with patch.object(create_puzzle.puzzle_creator, "create", return_value=puzzle) as mock_create:
        response = create_puzzle.lambda_handler(build_event({"imageUrl": image_url}), lambda_context)

    mock_create.assert_called_once_with(image_url)

    assert response["statusCode"] == 201
    assert response["headers"]["content-type"] == "application/json"

    body = json.loads(response["body"])
    assert body == {
        "id": str(puzzle.id),
        "name": puzzle.name,
        "format": puzzle.format,
        "hash": puzzle.hash,
        "createdAt": puzzle.created_at.isoformat().replace("+00:00", "Z"),
    }
