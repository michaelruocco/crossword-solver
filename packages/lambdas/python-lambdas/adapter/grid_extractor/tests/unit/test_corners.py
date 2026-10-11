import cv2
import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.corners import Corners


@pytest.fixture
def rectangle() -> Corners:
    return Corners(
        top_left=(20.0, 30.0),
        top_right=(180.0, 30.0),
        bottom_right=(180.0, 170.0),
        bottom_left=(20.0, 170.0),
    )


@pytest.fixture
def trapezoid() -> Corners:
    return Corners(
        top_left=(0.0, 0.0),
        top_right=(100.0, 0.0),
        bottom_right=(120.0, 50.0),
        bottom_left=(-20.0, 50.0),
    )


def test_center(rectangle):
    assert rectangle.center() == (100.0, 100.0)


def test_max_size_of_rectangle(rectangle):
    assert rectangle.max_size() == (160, 140)


def test_max_size_uses_longest_opposite_sides_truncated_to_whole_pixels(trapezoid):
    assert trapezoid.max_size() == (140, 53)


def test_perspective_transform_maps_corners_to_destination_rectangle(rectangle):
    transform = rectangle.perspective_transform(1.0)

    mapped = cv2.perspectiveTransform(
        np.array([[(20, 30), (180, 30), (180, 170), (20, 170)]], dtype=np.float32), transform
    )

    assert np.allclose(mapped[0], [(0, 0), (159, 0), (159, 139), (0, 139)])


def test_perspective_transform_expands_source_corners_away_from_center(rectangle):
    transform = rectangle.perspective_transform(2.0)

    expanded = np.array([[(-60, -40), (260, -40), (260, 240), (-60, 240)]], dtype=np.float32)
    mapped = cv2.perspectiveTransform(expanded, transform)

    assert np.allclose(mapped[0], [(0, 0), (159, 0), (159, 139), (0, 139)])


def test_draw_onto_marks_each_corner_in_red(rectangle):
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    rectangle.draw_onto(image)

    for x, y in [(20, 30), (180, 30), (180, 170), (20, 170)]:
        assert image[y, x + 10].tolist() == [0, 0, 255]
    assert image[100, 100].tolist() == [0, 0, 0]
