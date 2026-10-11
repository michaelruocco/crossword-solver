import pytest

from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id


def test_across():
    assert Id.across(3) == Id(3, Direction.ACROSS)


def test_down():
    assert Id.down(3) == Id(3, Direction.DOWN)


@pytest.mark.parametrize(
    ("clue_id", "expected"),
    [
        (Id.across(1), "1A"),
        (Id.down(12), "12D"),
    ],
)
def test_str(clue_id, expected):
    assert str(clue_id) == expected


def test_same_number_and_direction_are_equal_and_hash_alike():
    assert Id.across(1) == Id.across(1)
    assert hash(Id.across(1)) == hash(Id.across(1))


def test_same_number_with_different_direction_are_not_equal():
    assert Id.across(1) != Id.down(1)
