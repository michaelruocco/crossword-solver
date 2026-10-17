from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_create_puzzle.get_puzzle_summaries import get_puzzle_summaries_handler


def test_handler_returns_all_puzzle_summaries(build_event, lambda_context):
    summaries = [PuzzleSummary(uuid4(), "puzzle14", datetime(2026, 10, 17, 9, 30, tzinfo=UTC), 24)]

    with patch.object(
        get_puzzle_summaries_handler.puzzle_summary_lister, "list_all", return_value=summaries
    ) as list_all:
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    list_all.assert_called_once_with()
    assert response_status(response) == 200
    assert response_json(response) == [
        {
            "id": str(summaries[0].id),
            "name": "puzzle14",
            "createdAt": "2026-10-17T09:30:00Z",
            "clueCount": 24,
        }
    ]


def test_handler_returns_an_empty_array_when_no_puzzles_exist(build_event, lambda_context):
    with patch.object(get_puzzle_summaries_handler.puzzle_summary_lister, "list_all", return_value=[]):
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    assert response_status(response) == 200
    assert response_json(response) == []


def test_handler_returns_internal_server_error_when_listing_fails(build_event, lambda_context):
    with patch.object(get_puzzle_summaries_handler.puzzle_summary_lister, "list_all", side_effect=RuntimeError("boom")):
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
