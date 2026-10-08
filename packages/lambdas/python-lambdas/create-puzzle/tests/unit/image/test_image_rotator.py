import pytest
from PIL import Image

from crossword_solver_create_puzzle.create_puzzle.image.image_rotator import (
    ImageRotator,
)


@pytest.fixture
def rotator():
    return ImageRotator()


def test_does_not_rotate_normal_image(rotator):
    image = Image.new("RGB", (100, 50))

    result = rotator.rotate_if_required(image)

    assert result.size == (100, 50)


def test_rotates_180_degrees(rotator):
    image = Image.new("RGB", (100, 50))

    exif = image.getexif()
    exif[274] = 3
    image.info["exif"] = exif.tobytes()

    result = rotator.rotate_if_required(image)

    assert result.size == (100, 50)


def test_rotates_90_degrees_clockwise(rotator):
    image = Image.new("RGB", (100, 50))

    exif = image.getexif()
    exif[274] = 6
    image.info["exif"] = exif.tobytes()

    result = rotator.rotate_if_required(image)

    assert result.size == (50, 100)


def test_rotates_90_degrees_counter_clockwise(rotator):
    image = Image.new("RGB", (100, 50))

    exif = image.getexif()
    exif[274] = 8
    image.info["exif"] = exif.tobytes()

    result = rotator.rotate_if_required(image)

    assert result.size == (50, 100)
