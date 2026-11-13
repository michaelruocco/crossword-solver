from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.answers import Answers
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.words import Words

ACROSS_1 = Word(Id.across(1), 3, Coordinates(0, 2))
DOWN_1 = Word(Id.down(1), 3, Coordinates(2, 2))


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
    puzzle.clues.find.return_value = Clue(clue_id, "A clue", [3])
    puzzle.intersections.return_value = []
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


def test_accepts_answers_with_the_clue_length_and_ignores_whitespace_and_case():
    attempt = _attempt_with(
        [Clue(Id.across(1), "A clue", [3, 2])],
        [Word(Id.across(1), 5, Coordinates(0, 0))],
    )

    assert attempt.accepts(Answer(Id.across(1), "ab C de"))


def test_rejects_an_answer_with_the_wrong_length():
    attempt = _attempt_with(
        [Clue(Id.across(1), "A clue", [3])],
        [ACROSS_1],
    )

    assert not attempt.accepts(Answer(Id.across(1), "TOO LONG"))


def test_rejects_an_answer_for_a_clue_that_is_not_in_the_puzzle():
    attempt = _attempt_with([Clue(Id.across(1), "A clue", [3])], [ACROSS_1])

    assert not attempt.accepts(Answer(Id.down(9), "CAT"))


def test_accepts_an_answer_when_its_intersections_match_saved_answers():
    attempt = _attempt_with(
        [Clue(Id.across(1), "Across", [3]), Clue(Id.down(1), "Down", [3])],
        [ACROSS_1, DOWN_1],
        [Answer(Id.across(1), "CAT")],
    )

    assert attempt.accepts(Answer(Id.down(1), "TAR"))


def test_rejects_an_answer_when_an_intersection_conflicts_with_a_saved_answer():
    attempt = _attempt_with(
        [Clue(Id.across(1), "Across", [3]), Clue(Id.down(1), "Down", [3])],
        [ACROSS_1, DOWN_1],
        [Answer(Id.across(1), "CAT")],
    )

    assert not attempt.accepts(Answer(Id.down(1), "BAR"))


def test_checks_intersections_when_the_new_answer_is_across():
    attempt = _attempt_with(
        [Clue(Id.across(1), "Across", [3]), Clue(Id.down(1), "Down", [3])],
        [ACROSS_1, DOWN_1],
        [Answer(Id.down(1), "TAR")],
    )

    assert attempt.accepts(Answer(Id.across(1), "CAT"))
    assert not attempt.accepts(Answer(Id.across(1), "CAR"))


def _attempt_with(clues: list[Clue], words: list[Word], answers: list[Answer] | None = None) -> Attempt:
    puzzle = Puzzle(
        id=uuid4(),
        name="Test puzzle",
        format="",
        hash="",
        clues=Clues(clues),
        grid=Mock(),
        words=Words(words),
        created_at=datetime(2026, 10, 31, 9, 30, tzinfo=UTC),
    )
    return Attempt(
        id=uuid4(),
        created_at=datetime(2026, 10, 31, 9, 30, tzinfo=UTC),
        puzzle=puzzle,
        answers=Answers(answers),
    )
