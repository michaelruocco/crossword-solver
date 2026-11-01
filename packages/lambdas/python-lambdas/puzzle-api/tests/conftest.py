"""Unit tests configuration module."""

import os

from crossword_solver_test_utils.fixtures import build_event, build_s3_event, build_sqs_event, lambda_context  # noqa: F401

# The handler module builds a boto3 client at import time, which needs a region.
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("CLUE_EXTRACTOR_MODEL_ID", "test-model-id")
os.environ.setdefault("PUZZLES_TABLE_NAME", "puzzles")
os.environ.setdefault("ATTEMPTS_TABLE_NAME", "attempts")
os.environ.setdefault("PUZZLE_IMPORTS_TABLE_NAME", "puzzle-imports")
os.environ.setdefault("PUZZLE_IMAGES_BUCKET_NAME", "puzzle-images")
os.environ.setdefault("PUZZLE_IMPORT_QUEUE_URL", "https://sqs.eu-west-2.amazonaws.com/123456789012/puzzle-imports")
