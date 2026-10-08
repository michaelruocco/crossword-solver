import pytest

from crossword_solver_domain_entities.direction import Direction


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("A", Direction.ACROSS),
        ("D", Direction.DOWN),
        ("ACROSS", Direction.ACROSS),
        ("DOWN", Direction.DOWN),
        ("across", Direction.ACROSS),
        ("down", Direction.DOWN),
    ],
)
def test_parses_value_or_name(value, expected):
    assert Direction(value) == expected


def test_rejects_unknown_value():
    with pytest.raises(ValueError):
        Direction("SIDEWAYS")
