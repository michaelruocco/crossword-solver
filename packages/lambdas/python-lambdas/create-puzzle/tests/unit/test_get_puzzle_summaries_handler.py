from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary
from crossword_solver_domain_use_case.invalid_puzzle_summary_cursor_error import InvalidPuzzleSummaryCursorError
from crossword_solver_domain_use_case.puzzle_summary_page import PuzzleSummaryPage
from crossword_solver_test_utils.responses import response_json, response_status

from crossword_solver_create_puzzle.get_puzzle_summaries import get_puzzle_summaries_handler


def test_handler_returns_a_page_of_puzzle_summaries(build_event, lambda_context):
    summaries = [PuzzleSummary(uuid4(), "puzzle14", datetime(2026, 10, 17, 9, 30, tzinfo=UTC), 24)]
    page = PuzzleSummaryPage(summaries, "next-page")
    event = build_event(None)
    event["queryStringParameters"] = {"limit": "1", "cursor": "current-page"}

    with patch.object(get_puzzle_summaries_handler.puzzle_summary_lister, "list_page", return_value=page) as list_page:
        response = get_puzzle_summaries_handler.lambda_handler(event, lambda_context)

    list_page.assert_called_once_with(1, "current-page")
    assert response_status(response) == 200
    assert response_json(response) == {
        "summaries": [
            {
                "id": str(summaries[0].id),
                "name": "puzzle14",
                "createdAt": "2026-10-17T09:30:00Z",
                "clueCount": 24,
            }
        ],
        "nextCursor": "next-page",
    }


def test_handler_returns_an_empty_page_when_no_puzzles_exist(build_event, lambda_context):
    with patch.object(
        get_puzzle_summaries_handler.puzzle_summary_lister,
        "list_page",
        return_value=PuzzleSummaryPage([], None),
    ):
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    assert response_status(response) == 200
    assert response_json(response) == {"summaries": [], "nextCursor": None}


def test_handler_returns_bad_request_for_invalid_query(build_event, lambda_context):
    event = build_event(None)
    event["queryStringParameters"] = {"limit": "not-a-number"}

    with patch.object(get_puzzle_summaries_handler.puzzle_summary_lister, "list_page") as list_page:
        response = get_puzzle_summaries_handler.lambda_handler(event, lambda_context)

    list_page.assert_not_called()
    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid request"}


def test_handler_returns_bad_request_for_invalid_cursor(build_event, lambda_context):
    with patch.object(
        get_puzzle_summaries_handler.puzzle_summary_lister,
        "list_page",
        side_effect=InvalidPuzzleSummaryCursorError("invalid"),
    ):
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    assert response_status(response) == 400
    assert response_json(response) == {"message": "Invalid cursor"}


def test_handler_returns_internal_server_error_when_listing_fails(build_event, lambda_context):
    with patch.object(
        get_puzzle_summaries_handler.puzzle_summary_lister, "list_page", side_effect=RuntimeError("boom")
    ):
        response = get_puzzle_summaries_handler.lambda_handler(build_event(None), lambda_context)

    assert response_status(response) == 500
    assert response_json(response) == {"message": "Internal server error"}
