from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.answers import Answers
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.words import Words

from crossword_solver_domain_use_case.pattern_factory import PatternFactory


def test_adds_patterns_from_saved_answers_to_all_clues():
    across_clue = Clue(Id.across(1), "Across", [3])
    down_clue = Clue(Id.down(1), "Down", [3])
    clues = Clues([across_clue, down_clue])
    attempt = _attempt_with(
        clues,
        [
            Word(Id.across(1), 3, Coordinates(0, 0)),
            Word(Id.down(1), 3, Coordinates(1, 0)),
        ],
        [
            Answer(Id.across(1), "cAt"),
            Answer(Id.down(1), "aNt"),
        ],
    )

    patterned_clues = PatternFactory().add_patterns_to_clues(clues, attempt)

    patterned_across = patterned_clues.find(across_clue.id)
    patterned_down = patterned_clues.find(down_clue.id)
    original_across = clues.find(across_clue.id)
    original_down = clues.find(down_clue.id)
    assert patterned_across is not None
    assert patterned_down is not None
    assert original_across is not None
    assert original_down is not None
    assert patterned_across.pattern == "?A?"
    assert patterned_down.pattern == "A??"
    assert original_across.pattern == "???"
    assert original_down.pattern == "???"


def test_leaves_unknown_letters_when_there_are_no_saved_intersecting_answers():
    clue = Clue(Id.across(1), "Across", [3])
    clues = Clues([clue])
    attempt = _attempt_with(clues, [Word(Id.across(1), 3, Coordinates(0, 0))], [])

    patterned_clues = PatternFactory().add_patterns_to_clues(clues, attempt)

    patterned_clue = patterned_clues.find(clue.id)
    assert patterned_clue is not None
    assert patterned_clue.pattern == "???"


def test_leaves_unknown_letters_when_intersecting_answer_is_missing_or_too_short():
    across_clue = Clue(Id.across(1), "Across", [3])
    down_clue_with_short_answer = Clue(Id.down(1), "Down with short answer", [3])
    unanswered_down_clue = Clue(Id.down(2), "Unanswered down", [3])
    clues = Clues([across_clue, down_clue_with_short_answer, unanswered_down_clue])
    attempt = _attempt_with(
        clues,
        [
            Word(Id.across(1), 3, Coordinates(0, 0)),
            Word(Id.down(1), 3, Coordinates(1, 2)),
            Word(Id.down(2), 3, Coordinates(2, 0)),
        ],
        [Answer(Id.down(1), "A")],
    )

    patterned_clues = PatternFactory().add_patterns_to_clues(clues, attempt)

    patterned_across = patterned_clues.find(across_clue.id)
    assert patterned_across is not None
    assert patterned_across.pattern == "???"


def _attempt_with(clues: Clues, words: list[Word], answers: list[Answer]) -> Attempt:
    puzzle = Puzzle(
        id=uuid4(),
        name="Test puzzle",
        format="",
        hash="",
        clues=clues,
        grid=Mock(),
        words=Words(words),
        created_at=datetime(2026, 11, 28, tzinfo=UTC),
    )
    return Attempt(
        id=uuid4(),
        created_at=datetime(2026, 11, 28, tzinfo=UTC),
        puzzle=puzzle,
        answers=Answers(answers),
    )
