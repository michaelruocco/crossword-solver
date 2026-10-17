import json
from dataclasses import dataclass

import pytest


@dataclass
class FakeLambdaContext:
    function_name: str = "test-function"
    memory_limit_in_mb: int = 512
    invoked_function_arn: str = "arn:aws:lambda:eu-west-2:123456789012:function:test-function"
    aws_request_id: str = "request-id"


@pytest.fixture
def lambda_context() -> FakeLambdaContext:
    return FakeLambdaContext()


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


@pytest.fixture
def build_sqs_event():
    def _build_sqs_event(*bodies: str) -> dict:
        return {
            "Records": [
                {
                    "messageId": f"message-{index}",
                    "receiptHandle": "receipt-handle",
                    "body": body,
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1704067200000",
                        "SenderId": "sender-id",
                        "ApproximateFirstReceiveTimestamp": "1704067200001",
                    },
                    "messageAttributes": {},
                    "md5OfBody": "md5",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:eu-west-2:123456789012:puzzle-imports",
                    "awsRegion": "eu-west-2",
                }
                for index, body in enumerate(bodies)
            ]
        }

    return _build_sqs_event


@pytest.fixture
def build_s3_event():
    def _build_s3_event(*keys: str) -> dict:
        return {
            "Records": [
                {
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "eu-west-2",
                    "eventTime": "2024-01-01T00:00:00.000Z",
                    "eventName": "ObjectCreated:Post",
                    "userIdentity": {"principalId": "principal-id"},
                    "requestParameters": {"sourceIPAddress": "127.0.0.1"},
                    "responseElements": {"x-amz-request-id": "request-id", "x-amz-id-2": "id-2"},
                    "s3": {
                        "s3SchemaVersion": "1.0",
                        "configurationId": "configuration-id",
                        "bucket": {
                            "name": "puzzle-images",
                            "ownerIdentity": {"principalId": "principal-id"},
                            "arn": "arn:aws:s3:::puzzle-images",
                        },
                        "object": {"key": key, "size": 1024, "eTag": "etag", "sequencer": "sequencer"},
                    },
                }
                for key in keys
            ]
        }

    return _build_s3_event
