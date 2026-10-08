"""Unit tests configuration module."""

import os
import sys
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

# The handler module builds a boto3 client at import time, which needs a region.
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("CLUE_EXTRACTOR_MODEL_ID", "test-model-id")

# OpenCV and the tesseract binary come from Lambda layers, so stub them before the handler is imported.
sys.modules["cv2"] = MagicMock(__version__="0.0.0-test")
sys.modules["pytesseract"] = MagicMock(get_tesseract_version=MagicMock(return_value="0.0.0-test"))


@dataclass
class FakeLambdaContext:
    function_name: str = "create-puzzle"
    memory_limit_in_mb: int = 512
    invoked_function_arn: str = "arn:aws:lambda:eu-west-2:123456789012:function:create-puzzle"
    aws_request_id: str = "request-id"


@pytest.fixture
def lambda_context() -> FakeLambdaContext:
    return FakeLambdaContext()
