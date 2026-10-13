import cv2
import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.rects import contains, keep_outermost

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


def rectangle(x: int, y: int, width: int, height: int) -> np.ndarray:
    return np.array([[[x, y]], [[x + width - 1, y]], [[x + width - 1, y + height - 1]], [[x, y + height - 1]]])


def test_keep_outermost_removes_contours_inside_others():
    outer = rectangle(10, 10, 50, 50)
    inner = rectangle(20, 20, 10, 10)
    separate = rectangle(100, 10, 10, 10)

    kept = keep_outermost([inner, outer, separate])

    assert [cv2.boundingRect(contour) for contour in kept] == [(10, 10, 50, 50), (100, 10, 10, 10)]


def test_keep_outermost_keeps_first_of_contours_with_identical_bounds():
    first = rectangle(10, 10, 20, 20)
    second = rectangle(10, 10, 20, 20)

    kept = keep_outermost([first, second])

    assert len(kept) == 1
    assert kept[0] is first


def test_keep_outermost_keeps_overlapping_contours():
    left = rectangle(10, 10, 20, 20)
    right = rectangle(20, 10, 20, 20)

    assert len(keep_outermost([left, right])) == 2
