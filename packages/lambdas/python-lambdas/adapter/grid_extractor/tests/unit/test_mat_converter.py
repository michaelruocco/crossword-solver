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


@pytest.mark.parametrize("frames", [1, 2])
def test_selects_grid_nested_inside_page_frames(converter, frames):
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    for offset in range(10, 10 + frames * 25, 25):
        cv2.rectangle(image, (offset, offset), (399 - offset, 399 - offset), (0, 0, 0), 3)
    for position in range(120, 281, 40):
        cv2.line(image, (120, position), (280, position), (0, 0, 0), 3)
        cv2.line(image, (position, 120), (position, 280), (0, 0, 0), 3)

    cropped = converter.crop(image, 0)

    assert np.array_equal(cropped, image[118:283, 118:283])


def test_prefers_larger_grid_over_smaller_nested_pattern(converter):
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    for start, stop, spacing in [(20, 100, 20), (150, 350, 50)]:
        for position in range(start, stop + 1, spacing):
            cv2.line(image, (start, position), (stop, position), (0, 0, 0), 3)
            cv2.line(image, (position, start), (position, stop), (0, 0, 0), 3)

    assert np.array_equal(converter.crop(image, 0), image[148:353, 148:353])


def test_grid_selection_reports_blank_image(converter):
    with pytest.raises(ValueError, match="No contours found"):
        converter.crop(np.full((100, 100, 3), 255, dtype=np.uint8), 0)


GRID_LINES = range(50, 351, 75)


def binary_grid() -> np.ndarray:
    image = np.zeros((400, 400), dtype=np.uint8)
    for position in GRID_LINES:
        cv2.line(image, (50, position), (350, position), 255, 3)
        cv2.line(image, (position, 50), (position, 350), 255, 3)
    return image


def test_blur_softens_edges(converter):
    image = np.zeros((50, 50), dtype=np.uint8)
    image[:, 25:] = 255

    blurred = converter.blur(image)

    assert 0 < blurred[10, 23] < 255
    assert 0 < blurred[10, 26] < 255
    assert blurred[10, 0] == 0
    assert blurred[10, 49] == 255


def test_smooth_removes_specks_and_keeps_larger_shapes(converter):
    image = np.zeros((50, 50), dtype=np.uint8)
    image[10, 10] = 255
    image[30:40, 30:40] = 255

    smoothed = converter.smooth(image)

    assert smoothed[10, 10] == 0
    assert smoothed[35, 35] == 255


def test_remove_noise_smaller_than(converter):
    image = np.zeros((300, 300), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (260, 260), 255, 3)
    cv2.rectangle(image, (60, 60), (65, 65), 255, -1)
    cv2.rectangle(image, (100, 100), (200, 110), 255, -1)
    cv2.rectangle(image, (120, 150), (160, 190), 255, -1)
    cv2.rectangle(image, (270, 270), (290, 290), 255, -1)

    cleaned = converter.remove_noise_smaller_than(image, 1500)

    assert cleaned[62, 62] == 0, "small shape inside the grid is noise"
    assert cleaned[105, 150] == 255, "shape wider than the noise size limit is kept"
    assert cleaned[170, 140] == 255, "shape with area above the minimum is kept"
    assert cleaned[280, 280] == 0, "small shape outside the grid is noise"
    assert cleaned[20, 100] == 255, "grid outline is kept"
    assert image[62, 62] == 255, "input is not modified"


def test_noise_removal_preserves_disconnected_grid_sections(converter):
    image = np.zeros((300, 300), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (120, 120), 255, 3)
    cv2.rectangle(image, (160, 160), (260, 260), 255, 3)
    cv2.rectangle(image, (180, 180), (185, 185), 255, -1)
    cv2.rectangle(image, (270, 270), (280, 280), 255, -1)

    cleaned = converter.remove_noise_smaller_than(image, 1500)

    assert cleaned[20, 60] == 255
    assert cleaned[160, 200] == 255
    assert cleaned[182, 182] == 0
    assert cleaned[275, 275] == 0
    assert image[182, 182] == 255


def test_noise_removal_discards_large_artifacts_outside_a_grid_outline(converter):
    image = np.zeros((400, 400), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (260, 260), 255, 3)
    cv2.rectangle(image, (300, 300), (390, 390), 255, -1)

    cleaned = converter.remove_noise_smaller_than(image, 1500)

    assert cleaned[20, 100] == 255
    assert cleaned[345, 345] == 0


def test_to_horizontal_grid_lines_keeps_only_horizontal_lines(converter):
    horizontal = converter.to_horizontal_grid_lines(binary_grid())

    assert horizontal[125, 90] == 255
    assert horizontal[90, 125] == 0


def test_to_vertical_grid_lines_keeps_only_vertical_lines(converter):
    vertical = converter.to_vertical_grid_lines(binary_grid())

    assert vertical[90, 125] == 255
    assert vertical[125, 90] == 0


def test_combine_and_intersect():
    first = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    second = np.array([[0, 255], [0, 255]], dtype=np.uint8)
    converter = MatConverter()

    assert converter.combine(first, second).tolist() == [[0, 255], [255, 255]]
    assert converter.intersect(first, second).tolist() == [[0, 255], [0, 0]]


def test_to_points_finds_every_grid_intersection(converter):
    intersections = converter.to_intersections(binary_grid())

    points = converter.to_points(intersections)

    expected = {(x, y) for x in GRID_LINES for y in GRID_LINES}
    assert {(round(x), round(y)) for x, y in points} == expected


def test_to_points_skips_contours_with_no_area(converter):
    image = np.zeros((20, 20), dtype=np.uint8)
    image[5, 5:15] = 255

    assert converter.to_points(image) == []


def test_scale_enlarges_without_blending_pixels(converter):
    image = np.array([[0, 255]], dtype=np.uint8)

    scaled = converter.scale(image, 3)

    assert scaled.shape == (3, 6)
    assert set(np.unique(scaled)) == {0, 255}


def test_invert_swaps_black_and_white_and_returns_colour(converter):
    image = np.array([[0, 255]], dtype=np.uint8)

    inverted = converter.invert(image)

    assert inverted.tolist() == [[[255, 255, 255], [0, 0, 0]]]
