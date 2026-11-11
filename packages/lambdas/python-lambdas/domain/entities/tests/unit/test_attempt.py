from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id
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


def test_saving_answer_adds_it_and_increments_count_once_per_clue():
    clue_id = Id.across(3)
    puzzle = Mock(spec=Puzzle)
    puzzle.id = uuid4()
    puzzle.clues = Mock()
    puzzle.clues.has_clue.return_value = True
    attempt = Attempt(
        id=uuid4(),
        created_at=datetime(2026, 10, 31, 9, 30, tzinfo=UTC),
        puzzle=puzzle,
    )

    answered = attempt.save_answer(Answer(clue_id, "CAT"))
    changed = answered.save_answer(Answer(clue_id, "DOG"))

    assert attempt.answer_count == 0
    assert answered.answer_count == 1
    assert answered.answers.find(clue_id) == Answer(clue_id, "CAT")
    assert changed.answer_count == 1
    assert changed.answers.find(clue_id) == Answer(clue_id, "DOG")


def test_saving_answer_rejects_a_clue_not_in_the_puzzle():
    clue_id = Id.down(1)
    puzzle = Mock(spec=Puzzle)
    puzzle.id = uuid4()
    puzzle.clues = Mock()
    puzzle.clues.has_clue.return_value = False
    attempt = Attempt(
        id=uuid4(),
        created_at=datetime(2026, 10, 31, 9, 30, tzinfo=UTC),
        puzzle=puzzle,
    )

    with pytest.raises(ClueNotFoundForIdError) as error:
        attempt.save_answer(Answer(clue_id, "CAT"))

    assert error.value.clue_id == clue_id
