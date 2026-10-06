"""Unit tests configuration module."""

from dataclasses import dataclass

import pytest


@dataclass
class FakeLambdaContext:
    function_name: str = "create-puzzle"
    memory_limit_in_mb: int = 512
    invoked_function_arn: str = "arn:aws:lambda:eu-west-2:123456789012:function:create-puzzle"
    aws_request_id: str = "request-id"


@pytest.fixture
def lambda_context() -> FakeLambdaContext:
    return FakeLambdaContext()
