import pytest
from crossword_solver_domain_use_case.image_error import ImageError
from pytest_httpserver import HTTPServer

from crossword_solver_adapter_web.web_image_fetcher import WebImageFetcher

IMAGE_BYTES = bytes(range(256)) * 8
MAX_BYTES = 10 * 1024 * 1024


@pytest.fixture
def fetcher() -> WebImageFetcher:
    return WebImageFetcher()


def test_fetch_returns_filename_from_the_url_and_the_content(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/images/puzzle24.jpg").respond_with_data(IMAGE_BYTES, content_type="image/jpeg")

    file = fetcher.fetch(httpserver.url_for("/images/puzzle24.jpg?size=large"), MAX_BYTES)

    assert file.filename == "puzzle24.jpg"
    assert file.content == IMAGE_BYTES


def test_fetch_accepts_an_image_of_exactly_the_maximum_size(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/puzzle24.jpg").respond_with_data(b"x" * 100)

    assert len(fetcher.fetch(httpserver.url_for("/puzzle24.jpg"), 100).content) == 100


def test_fetch_stops_reading_one_byte_over_the_maximum_size(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/puzzle24.jpg").respond_with_data(b"x" * 500)

    assert len(fetcher.fetch(httpserver.url_for("/puzzle24.jpg"), 100).content) == 101


@pytest.mark.parametrize("status", [404, 500])
def test_fetch_raises_error_when_the_server_responds_with_an_error(fetcher, httpserver: HTTPServer, status):
    httpserver.expect_request("/puzzle24.jpg").respond_with_data("", status=status)
    url = httpserver.url_for("/puzzle24.jpg")

    with pytest.raises(ImageError, match="Failed to download image"):
        fetcher.fetch(url, MAX_BYTES)


def test_fetch_raises_error_when_the_connection_fails(fetcher):
    with pytest.raises(ImageError, match="Failed to download image"):
        fetcher.fetch("http://localhost:1/puzzle24.jpg", MAX_BYTES)


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/puzzle24.jpg", "puzzle24.jpg"])
def test_fetch_raises_error_for_unsupported_scheme(fetcher, url):
    with pytest.raises(ImageError, match="Unsupported image URL scheme"):
        fetcher.fetch(url, MAX_BYTES)
