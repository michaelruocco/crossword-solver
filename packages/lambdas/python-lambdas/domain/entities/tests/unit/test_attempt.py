from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.puzzle import Puzzle


def test_attempt_defaults_to_an_empty_unsolved_attempt():
    attempt_id = uuid4()
    created_at = datetime(2026, 10, 31, 9, 30, tzinfo=UTC)
    puzzle = Mock(spec=Puzzle)
    puzzle.id = uuid4()

    attempt = Attempt(id=attempt_id, created_at=created_at, puzzle=puzzle)

    assert attempt.id == attempt_id
    assert attempt.created_at == created_at
    assert attempt.puzzle is puzzle
    assert attempt.puzzle_id == puzzle.id
    assert attempt.solving is False
    assert attempt.answer_count == 0


def test_attempt_preserves_explicit_solving_state_and_answer_count():
    puzzle = Mock(spec=Puzzle)
    attempt = Attempt(
        id=uuid4(),
        created_at=datetime(2026, 10, 31, 9, 30, tzinfo=UTC),
        puzzle=puzzle,
        solving=True,
        answer_count=3,
    )

    assert attempt.solving is True
    assert attempt.answer_count == 3
