from io import BytesIO

import pytest
from crossword_solver_domain_use_case.image_error import ImageError
from PIL import Image as PILImage
from pytest_httpserver import HTTPServer

from crossword_solver_image.default_image_downloader import (
    DefaultImageDownloader,
)


@pytest.fixture
def downloader():
    return DefaultImageDownloader()


@pytest.fixture
def jpeg_bytes() -> bytes:
    buffer = BytesIO()
    PILImage.new("RGB", (10, 10), "white").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_download_image(downloader, httpserver: HTTPServer, jpeg_bytes):
    httpserver.expect_request("/images/puzzle24.jpg").respond_with_data(jpeg_bytes, content_type="image/jpeg")

    image = downloader.download_image(httpserver.url_for("/images/puzzle24.jpg"))

    assert image.name == "puzzle24"
    assert image.format == ".jpg"
    assert image.pil_image.size == (10, 10)
    assert image.bytes
    assert image.hash


def test_download_image_not_found(downloader, httpserver: HTTPServer):
    httpserver.expect_request("/images/does-not-exist.jpg").respond_with_data("", status=404)

    with pytest.raises(ImageError, match="Failed to download image"):
        downloader.download_image(httpserver.url_for("/images/does-not-exist.jpg"))


def test_download_image_not_an_image(downloader, httpserver: HTTPServer):
    httpserver.expect_request("/images/puzzle24.jpg").respond_with_data("<html></html>", content_type="text/html")

    with pytest.raises(ImageError, match="Failed to decode image"):
        downloader.download_image(httpserver.url_for("/images/puzzle24.jpg"))
