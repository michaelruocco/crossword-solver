"""Unit tests configuration module."""

import os

from crossword_solver_test_utils.fixtures import build_sqs_event, lambda_context  # noqa: F401

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("CLUE_EXTRACTOR_MODEL_ID", "test-model-id")
os.environ.setdefault("TESSDATA_PREFIX", "/opt/share/tessdata")
os.environ.setdefault("PUZZLES_TABLE_NAME", "puzzles")
os.environ.setdefault("PUZZLE_IMPORTS_TABLE_NAME", "puzzle-imports")
os.environ.setdefault("PUZZLE_IMAGES_BUCKET_NAME", "puzzle-images")
