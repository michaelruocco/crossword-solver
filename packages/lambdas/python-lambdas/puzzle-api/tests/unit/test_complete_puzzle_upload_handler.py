from unittest.mock import patch
from uuid import uuid4

import pytest

from crossword_solver_puzzle_api.complete_puzzle_upload import complete_puzzle_upload_handler


def test_handler_completes_the_import_for_each_uploaded_file(build_s3_event, lambda_context):
    first, second = uuid4(), uuid4()
    event = build_s3_event(f"uploads/{first}/puzzle+14.png", f"uploads/{second}/puzzle.jpg")

    with patch.object(complete_puzzle_upload_handler.puzzle_upload_completer, "complete") as complete:
        complete_puzzle_upload_handler.lambda_handler(event, lambda_context)

    assert [call.args[0] for call in complete.call_args_list] == [first, second]


def test_handler_lets_errors_propagate_so_the_notification_is_retried(build_s3_event, lambda_context):
    event = build_s3_event(f"uploads/{uuid4()}/puzzle.png")

    with (
        patch.object(
            complete_puzzle_upload_handler.puzzle_upload_completer, "complete", side_effect=RuntimeError("boom")
        ),
        pytest.raises(RuntimeError, match="boom"),
    ):
        complete_puzzle_upload_handler.lambda_handler(event, lambda_context)


def test_handler_rejects_keys_that_are_not_uploads(build_s3_event, lambda_context):
    event = build_s3_event("images/puzzle.png")

    with (
        patch.object(complete_puzzle_upload_handler.puzzle_upload_completer, "complete") as complete,
        pytest.raises(ValueError, match="Not an upload key"),
    ):
        complete_puzzle_upload_handler.lambda_handler(event, lambda_context)

    complete.assert_not_called()
