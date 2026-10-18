import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from crossword_solver_puzzle_import_worker import process_puzzle_import_handler


def test_handler_processes_each_import_in_the_batch(build_sqs_event, lambda_context):
    first, second = uuid4(), uuid4()
    event = build_sqs_event(json.dumps({"importId": str(first)}), json.dumps({"importId": str(second)}))

    with patch.object(process_puzzle_import_handler.puzzle_import_processor, "process") as process:
        process_puzzle_import_handler.lambda_handler(event, lambda_context)

    assert [call.args[0] for call in process.call_args_list] == [first, second]


def test_handler_lets_processing_errors_propagate_so_the_message_is_retried(build_sqs_event, lambda_context):
    event = build_sqs_event(json.dumps({"importId": str(uuid4())}))

    with (
        patch.object(
            process_puzzle_import_handler.puzzle_import_processor, "process", side_effect=RuntimeError("boom")
        ),
        pytest.raises(RuntimeError, match="boom"),
    ):
        process_puzzle_import_handler.lambda_handler(event, lambda_context)


def test_handler_rejects_message_without_an_import_id(build_sqs_event, lambda_context):
    event = build_sqs_event(json.dumps({"unexpected": "value"}))

    with (
        patch.object(process_puzzle_import_handler.puzzle_import_processor, "process") as process,
        pytest.raises(ValidationError),
    ):
        process_puzzle_import_handler.lambda_handler(event, lambda_context)

    process.assert_not_called()
