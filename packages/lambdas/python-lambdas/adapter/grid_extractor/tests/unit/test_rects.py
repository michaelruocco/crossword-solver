import pytest

from crossword_solver_adapter_grid_extractor.rects import contains

OUTER = (10, 20, 100, 50)


@pytest.mark.parametrize(
    "inner",
    [
        (30, 30, 10, 10),
        OUTER,
        (10, 20, 1, 1),
        (109, 69, 1, 1),
    ],
    ids=["strictly inside", "identical", "touching top left", "touching bottom right"],
)
def test_contains_when_inner_is_within_outer_including_edges(inner):
    assert contains(OUTER, inner)


@pytest.mark.parametrize(
    "inner",
    [
        (9, 30, 10, 10),
        (30, 19, 10, 10),
        (101, 30, 10, 10),
        (30, 61, 10, 10),
        (0, 0, 200, 200),
    ],
    ids=["past left", "past top", "past right", "past bottom", "surrounds outer"],
)
def test_does_not_contain_when_inner_extends_beyond_outer(inner):
    assert not contains(OUTER, inner)
