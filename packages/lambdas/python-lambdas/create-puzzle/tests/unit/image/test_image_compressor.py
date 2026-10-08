from io import BytesIO

from PIL import Image

from crossword_solver_create_puzzle.create_puzzle.image.image_compressor import (
    ImageCompressor,
)


def create_image(
    width: int = 200,
    height: int = 200,
    mode: str = "RGB",
) -> Image.Image:
    return Image.new(mode, (width, height), "white")


def test_should_compress_image_to_jpeg():
    compressor = ImageCompressor()

    result = compressor.compress_and_resize(create_image())

    with Image.open(BytesIO(result)) as image:
        assert image.format == "JPEG"


def test_should_not_resize_image_when_under_max_size():
    compressor = ImageCompressor(
        max_size_bytes=4 * 1024 * 1024,
    )
    image = create_image(500, 400)

    result = compressor.compress_and_resize(image)

    with Image.open(BytesIO(result)) as compressed:
        assert compressed.size == (500, 400)


def test_should_resize_image_when_over_max_size():
    compressor = ImageCompressor(
        max_size_bytes=1_000,
    )
    image = create_image(1_000, 1_000)

    result = compressor.compress_and_resize(image)

    with Image.open(BytesIO(result)) as compressed:
        assert compressed.width < 1_000
        assert compressed.height < 1_000


def test_should_compress_image_until_under_max_size():
    max_size_bytes = 10_000
    compressor = ImageCompressor(
        max_size_bytes=max_size_bytes,
    )
    image = create_image(1_000, 1_000)

    result = compressor.compress_and_resize(image)

    assert len(result) <= max_size_bytes


def test_should_convert_rgba_image_to_rgb():
    compressor = ImageCompressor()

    image = create_image(mode="RGBA")

    result = compressor.compress_and_resize(image)

    with Image.open(BytesIO(result)) as compressed:
        assert compressed.mode == "RGB"