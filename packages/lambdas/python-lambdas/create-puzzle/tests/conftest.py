"""Unit tests configuration module."""

import json
import os
from dataclasses import dataclass

import pytest

# The handler module builds a boto3 client at import time, which needs a region.
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("CLUE_EXTRACTOR_MODEL_ID", "test-model-id")


@dataclass
class FakeLambdaContext:
    function_name: str = "create-puzzle"
    memory_limit_in_mb: int = 512
    invoked_function_arn: str = "arn:aws:lambda:eu-west-2:123456789012:function:create-puzzle"
    aws_request_id: str = "request-id"


@pytest.fixture
def lambda_context() -> FakeLambdaContext:
    return FakeLambdaContext()


@pytest.fixture
def build_event():
    def _build_event(body: dict | None) -> dict:
        event = {
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
        if body is not None:
            event["body"] = json.dumps(body)
        return event

    return _build_event
