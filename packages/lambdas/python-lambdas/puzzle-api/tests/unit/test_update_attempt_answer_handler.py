from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_puzzle_api.update_attempt_answer import update_attempt_answer_handler


def test_handler_saves_answer_and_returns_updated_attempt(build_event, lambda_context):
    puzzle_id = uuid4()
    attempt_id = uuid4()
    attempt = MagicMock()
    attempt_converter = MagicMock()
    attempt_converter.to_response.return_value.model_dump_json.return_value = '{"id":"attempt-id","answerCount":1}'

    with (
        patch.object(update_attempt_answer_handler, "attempt_answer_saver") as saver,
        patch.object(update_attempt_answer_handler, "attempt_finder") as finder,
        patch.object(update_attempt_answer_handler, "attempt_converter", attempt_converter),
    ):
        finder.find_by_id.return_value = attempt
        response = update_attempt_answer_handler.lambda_handler(
            build_event(
                {"id": "3A", "value": "CAT"},
                {"puzzleId": str(puzzle_id), "attemptId": str(attempt_id)},
            ),
            lambda_context,
        )

    saver.save.assert_called_once()
    saved_answer = saver.save.call_args.args[2]
    assert str(saved_answer.id) == "3A"
    assert saved_answer.value == "CAT"
    finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt_converter.to_response.assert_called_once_with(attempt)
    assert response_status(response) == 200
    assert response_json(response) == {"id": "attempt-id", "answerCount": 1}


@pytest.mark.parametrize(
    ("path_parameters", "expected_message"),
    [
        ({"puzzleId": "invalid", "attemptId": str(uuid4())}, "Puzzle not found"),
        ({"puzzleId": str(uuid4()), "attemptId": "invalid"}, "Attempt not found"),
    ],
)
def test_handler_returns_not_found_for_invalid_path_ids(build_event, lambda_context, path_parameters, expected_message):
    with patch.object(update_attempt_answer_handler, "attempt_answer_saver") as saver:
        response = update_attempt_answer_handler.lambda_handler(
            build_event({"id": "3A", "value": "CAT"}, path_parameters),
            lambda_context,
        )

    saver.save.assert_not_called()
    assert response_status(response) == 404
    assert response_json(response) == {"message": expected_message}


@pytest.mark.parametrize(
    ("body", "path_parameters"),
    [
        (None, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
        ({"id": "3X", "value": "CAT"}, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
        ({"id": "3A"}, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
    ],
)
def test_handler_returns_bad_request_for_invalid_answer(build_event, lambda_context, body, path_parameters):
    response = update_attempt_answer_handler.lambda_handler(build_event(body, path_parameters), lambda_context)

    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid answer request"}


def test_handler_returns_not_found_when_attempt_does_not_exist(build_event, lambda_context):
    with patch.object(
        update_attempt_answer_handler.attempt_answer_saver,
        "save",
        side_effect=AttemptNotFoundError(uuid4(), uuid4()),
    ):
        response = update_attempt_answer_handler.lambda_handler(
            build_event({"id": "3A", "value": "CAT"}, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": "Attempt not found"}


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (PuzzleNotFoundError(uuid4()), "Puzzle not found"),
        (ClueNotFoundForIdError(Id.across(3)), "Clue not found"),
    ],
)
def test_handler_returns_not_found_for_puzzle_or_clue(build_event, lambda_context, error, expected_message):
    with patch.object(update_attempt_answer_handler.attempt_answer_saver, "save", side_effect=error):
        response = update_attempt_answer_handler.lambda_handler(
            build_event({"id": "3A", "value": "CAT"}, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 404
    assert response_json(response) == {"message": expected_message}


def test_handler_returns_internal_server_error_when_save_fails(build_event, lambda_context):
    with patch.object(update_attempt_answer_handler.attempt_answer_saver, "save", side_effect=RuntimeError("boom")):
        response = update_attempt_answer_handler.lambda_handler(
            build_event({"id": "3A", "value": "CAT"}, {"puzzleId": str(uuid4()), "attemptId": str(uuid4())}),
            lambda_context,
        )

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
