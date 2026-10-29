from io import BytesIO

import pytest
from crossword_solver_domain_use_case.image_error import ImageError
from PIL import Image as PILImage

from crossword_solver_image.image_factory import ImageFactory

URL = "s3://puzzle-images/images/abc/puzzle24.jpg"


@pytest.fixture
def jpeg_bytes() -> bytes:
    buffer = BytesIO()
    PILImage.new("RGB", (10, 10), "white").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_to_image_builds_image_from_url_and_bytes(jpeg_bytes):
    image = ImageFactory().to_image(URL, jpeg_bytes)

    assert image.name == "puzzle24"
    assert image.format == ".jpg"
    assert image.pil_image.size == (10, 10)
    assert image.bytes == jpeg_bytes
    assert len(image.hash) == 64


def test_to_image_hashes_the_original_bytes(jpeg_bytes):
    factory = ImageFactory()

    assert factory.to_image(URL, jpeg_bytes).hash == factory.hash_factory.to_hash(jpeg_bytes)


def test_to_image_decodes_webp_bytes():
    buffer = BytesIO()
    PILImage.new("RGB", (10, 10), "white").save(buffer, format="WEBP")
    image_bytes = buffer.getvalue()

    image = ImageFactory().to_image("s3://puzzle-images/images/abc/puzzle.webp", image_bytes)

    assert image.name == "puzzle"
    assert image.format == ".webp"
    assert image.pil_image.size == (10, 10)
    assert image.pil_image.getpixel((0, 0)) == (255, 255, 255)
    assert image.bytes == image_bytes


def test_to_image_raises_error_when_bytes_are_not_an_image():
    factory = ImageFactory()

    with pytest.raises(ImageError, match="Failed to decode image"):
        factory.to_image(URL, b"<html></html>")
