from datetime import UTC, datetime
from uuid import uuid4

from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from crossword_solver_adapter_api.puzzle_summary_converter import PuzzleSummaryConverter


def test_to_response_uses_the_api_field_names():
    summary = PuzzleSummary(uuid4(), "puzzle14", datetime(2026, 10, 17, 9, 30, tzinfo=UTC), 24)

    response = PuzzleSummaryConverter().to_response(summary)

    assert response.model_dump(by_alias=True, mode="json") == {
        "id": str(summary.id),
        "name": "puzzle14",
        "createdAt": "2026-10-17T09:30:00Z",
        "clueCount": 24,
    }
