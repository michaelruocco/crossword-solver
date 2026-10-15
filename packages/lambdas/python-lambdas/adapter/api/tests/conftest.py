"""Unit tests configuration module."""

import json

import pytest


@pytest.fixture
def build_event():
    def _build_event(body: dict | None, path_parameters: dict[str, str] | None = None) -> dict:
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
        if path_parameters is not None:
            event["pathParameters"] = path_parameters
        return event

    return _build_event
