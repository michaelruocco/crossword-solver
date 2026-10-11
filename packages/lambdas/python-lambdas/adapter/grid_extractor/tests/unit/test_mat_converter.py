import cv2
import numpy as np
import pytest

from crossword_solver_adapter_grid_extractor.corners import Corners
from crossword_solver_adapter_grid_extractor.mat_converter import MatConverter

TOP_LEFT = (20.0, 30.0)
TOP_RIGHT = (180.0, 30.0)
BOTTOM_RIGHT = (180.0, 170.0)
BOTTOM_LEFT = (20.0, 170.0)


@pytest.fixture
def converter() -> MatConverter:
    return MatConverter()


def outlined_rectangle() -> np.ndarray:
    image = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.rectangle(image, (20, 30), (180, 170), (0, 0, 0), 3)
    return image


def filled_rectangles() -> np.ndarray:
    image = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(image, (20, 30), (180, 170), 255, -1)
    cv2.rectangle(image, (185, 185), (195, 195), 255, -1)
    return image


def test_to_grayscale_returns_single_channel_image(converter):
    gray = converter.to_grayscale(outlined_rectangle())

    assert gray.shape == (200, 200)
    assert gray.dtype == np.uint8


def test_to_binary_marks_dark_lines_white_and_background_black(converter):
    gray = converter.to_grayscale(outlined_rectangle())

    binary = converter.to_binary(gray)

    assert binary[30, 100] == 255
    assert binary[100, 100] == 0


def test_to_contours_returns_only_external_contours(converter):
    contours = converter.to_contours(filled_rectangles())

    assert len(contours) == 2


def test_to_largest_contour_picks_biggest_area(converter):
    contour = converter.to_largest_contour(filled_rectangles())

    assert cv2.boundingRect(contour) == (20, 30, 161, 141)


def test_to_largest_contour_raises_error_when_no_contours(converter):
    blank = np.zeros((50, 50), dtype=np.uint8)

    with pytest.raises(ValueError, match="No contours found"):
        converter.to_largest_contour(blank)


def test_to_polygon_points_returns_rectangle_corners(converter):
    contour = converter.to_largest_contour(filled_rectangles())

    points = converter.to_polygon_points(contour)

    assert set(points) == {TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT}


@pytest.mark.parametrize(
    "points",
    [
        [TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT],
        [BOTTOM_RIGHT, TOP_LEFT, BOTTOM_LEFT, TOP_RIGHT],
        [BOTTOM_LEFT, BOTTOM_RIGHT, TOP_RIGHT, TOP_LEFT],
    ],
)
def test_order_corners_is_independent_of_input_order(converter, points):
    corners = converter.order_corners(points)

    assert corners == Corners(
        top_left=TOP_LEFT,
        top_right=TOP_RIGHT,
        bottom_right=BOTTOM_RIGHT,
        bottom_left=BOTTOM_LEFT,
    )


def test_order_corners_handles_skewed_quadrilateral(converter):
    corners = converter.order_corners([(30.0, 10.0), (190.0, 25.0), (175.0, 160.0), (10.0, 140.0)])

    assert corners == Corners(
        top_left=(30.0, 10.0),
        top_right=(190.0, 25.0),
        bottom_right=(175.0, 160.0),
        bottom_left=(10.0, 140.0),
    )


def skewed_grid() -> np.ndarray:
    image = np.full((300, 400, 3), 255, dtype=np.uint8)
    outline = np.array([(60, 50), (340, 40), (350, 260), (50, 250)], dtype=np.int32)
    cv2.polylines(image, [outline], True, (0, 0, 0), 6)
    return image


def test_warp_grid_output_is_sized_to_the_longest_grid_sides(converter):
    warped = converter.warp_grid(skewed_grid())

    height, width, channels = warped.shape
    assert 300 <= width <= 310
    assert 220 <= height <= 230
    assert channels == 3


def test_warp_grid_straightens_the_grid(converter):
    warped = converter.warp_grid(skewed_grid())

    contour = converter.to_largest_contour(converter.to_binary(converter.to_grayscale(warped), c=5))
    corners = converter.order_corners(converter.to_polygon_points(contour))

    assert corners.top_left[0] == pytest.approx(corners.bottom_left[0], abs=2)
    assert corners.top_right[0] == pytest.approx(corners.bottom_right[0], abs=2)
    assert corners.top_left[1] == pytest.approx(corners.top_right[1], abs=2)
    assert corners.bottom_left[1] == pytest.approx(corners.bottom_right[1], abs=2)


def test_crop_returns_grid_bounds_when_not_expanded(converter):
    image = outlined_rectangle()

    cropped = converter.crop(image, 0)

    assert cropped.shape == (145, 165, 3)
    assert np.array_equal(cropped, image[28:173, 18:183])


def test_crop_expands_bounds_on_every_side(converter):
    cropped = converter.crop(outlined_rectangle(), 10)

    assert cropped.shape == (165, 185, 3)


def test_crop_is_limited_to_image_bounds(converter):
    image = outlined_rectangle()

    cropped = converter.crop(image, 100)

    assert np.array_equal(cropped, image)


def test_crop_limits_expansion_at_the_edge_the_grid_is_closest_to(converter):
    image = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.rectangle(image, (20, 30), (190, 170), (0, 0, 0), 3)

    cropped = converter.crop(image, 15)

    assert cropped.shape == (175, 197, 3)
    assert np.array_equal(cropped, image[13:188, 3:200])
