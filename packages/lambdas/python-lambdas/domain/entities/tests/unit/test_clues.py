import pytest

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id

ACROSS_1 = Clue(id=Id.across(1), text="Pacific republic (4)", lengths=[4])
ACROSS_3 = Clue(id=Id.across(3), text="Stale (3,3)", lengths=[3, 3])
DOWN_1 = Clue(id=Id.down(1), text="Muscular twitch (4)", lengths=[4])


@pytest.fixture
def clues() -> Clues:
    return Clues([ACROSS_1, DOWN_1, ACROSS_3])


def test_iterates_in_insertion_order(clues):
    assert list(clues) == [ACROSS_1, DOWN_1, ACROSS_3]


def test_len(clues):
    assert len(clues) == 3


def test_empty():
    assert len(Clues([])) == 0


def test_later_clue_with_same_id_replaces_earlier():
    replacement = Clue(id=Id.across(1), text="Replacement (4)", lengths=[4])

    clues = Clues([ACROSS_1, replacement])

    assert list(clues) == [replacement]


def test_find_returns_clue(clues):
    assert clues.find(Id.down(1)) == DOWN_1


def test_find_returns_none_when_missing(clues):
    assert clues.find(Id.down(3)) is None


def test_has_clue(clues):
    assert clues.has_clue(Id.across(3))


def test_has_clue_is_false_when_direction_differs(clues):
    assert not clues.has_clue(Id.down(3))


def test_get_across(clues):
    assert list(clues.get_across()) == [ACROSS_1, ACROSS_3]


def test_get_down(clues):
    assert list(clues.get_down()) == [DOWN_1]


def test_with_type_sets_type_on_every_clue(clues):
    typed = clues.with_type(ClueType.CRYPTIC)

    assert [clue.type for clue in typed] == [ClueType.CRYPTIC] * 3
    assert [clue.id for clue in typed] == [ACROSS_1.id, DOWN_1.id, ACROSS_3.id]


def test_with_type_does_not_change_original(clues):
    clues.with_type(ClueType.CRYPTIC)

    assert [clue.type for clue in clues] == [None] * 3


def test_normalize_text_hyphens():
    clues = Clues([Clue(id=Id.across(1), text="Well\u2013known (4)", lengths=[4])])

    normalized = clues.normalize_text_hyphens()

    assert [clue.text for clue in normalized] == ["Well-known (4)"]
