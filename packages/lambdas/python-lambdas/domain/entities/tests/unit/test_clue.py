import pytest

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id


@pytest.fixture
def clue() -> Clue:
    return Clue(id=Id.down(7), text="Stale \u2013 old (3,3)", lengths=[3, 3], type=ClueType.STANDARD)


def test_numeric_id(clue):
    assert clue.numeric_id == 7


def test_direction(clue):
    assert clue.direction == Direction.DOWN


@pytest.mark.parametrize(
    ("lengths", "expected"),
    [
        ([4], 4),
        ([3, 3], 6),
        ([2, 1, 5], 8),
    ],
)
def test_total_length(lengths, expected):
    assert Clue(id=Id.across(1), text="text", lengths=lengths).total_length == expected


def test_type_defaults_to_none():
    assert Clue(id=Id.across(1), text="text", lengths=[4]).type is None


def test_with_type_changes_only_type(clue):
    typed = clue.with_type(ClueType.CRYPTIC)

    assert typed == Clue(id=clue.id, text=clue.text, lengths=clue.lengths, type=ClueType.CRYPTIC)


def test_normalize_hyphens_changes_only_text(clue):
    normalized = clue.normalize_hyphens()

    assert normalized == Clue(id=clue.id, text="Stale - old (3,3)", lengths=clue.lengths, type=clue.type)
