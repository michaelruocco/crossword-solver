from io import BytesIO

import pytest
from PIL import Image

from crossword_solver_image.image_converter import (
    ImageConverter,
)


@pytest.fixture
def converter():
    return ImageConverter()


def test_to_rgb_returns_existing_rgb_image(converter):
    image = Image.new("RGB", (2, 2))

    result = converter.to_rgb(image)

    assert result is image
    assert result.mode == "RGB"


def test_to_rgb_converts_image_to_rgb(converter):
    image = Image.new("RGBA", (2, 2), (255, 0, 0, 128))

    result = converter.to_rgb(image)

    assert result.mode == "RGB"
    assert result.size == (2, 2)


def test_to_rgb_uses_white_background_for_transparent_pixels(converter):
    image = Image.new("RGBA", (1, 1), (255, 0, 0, 0))

    result = converter.to_rgb(image)

    assert result.getpixel((0, 0)) == (255, 255, 255)


def test_to_bytes_returns_png(converter):
    image = Image.new("RGB", (2, 2), (255, 0, 0))

    result = converter.to_bytes(image)

    assert isinstance(result, bytes)

    decoded = Image.open(BytesIO(result))

    assert decoded.format == "PNG"
    assert decoded.size == (2, 2)
    assert decoded.mode == "RGB"
