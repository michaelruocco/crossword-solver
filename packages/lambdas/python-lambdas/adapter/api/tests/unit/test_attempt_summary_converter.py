from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from crossword_solver_adapter_api.attempt_summary_converter import AttemptSummaryConverter


def test_to_response_includes_summary_fields_and_clue_count():
    attempt = SimpleNamespace(
        id=uuid4(),
        created_at=datetime(2026, 11, 1, 12, 0, tzinfo=UTC),
        solving=True,
        answer_count=3,
        puzzle=SimpleNamespace(clues=[object(), object()]),
    )

    response = AttemptSummaryConverter().to_response(attempt)

    assert response.model_dump(by_alias=True, mode="json") == {
        "id": str(attempt.id),
        "createdAt": "2026-11-01T12:00:00Z",
        "solving": True,
        "answerCount": 3,
        "clueCount": 2,
    }
