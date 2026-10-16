import pytest
from crossword_solver_domain_use_case.image_error import ImageError
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Response

from crossword_solver_adapter_web.web_image_fetcher import WebImageFetcher

IMAGE_BYTES = bytes(range(256)) * 8
MAX_BYTES = 10 * 1024 * 1024


def allow_any_address(_address) -> bool:
    return True


@pytest.fixture
def fetcher() -> WebImageFetcher:
    # The test server listens on loopback, which the default policy rightly refuses.
    return WebImageFetcher(is_allowed=allow_any_address)


def test_fetch_returns_filename_from_the_url_and_the_content(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/images/puzzle24.jpg").respond_with_data(IMAGE_BYTES, content_type="image/jpeg")

    file = fetcher.fetch(httpserver.url_for("/images/puzzle24.jpg?size=large"), MAX_BYTES)

    assert file.filename == "puzzle24.jpg"
    assert file.content == IMAGE_BYTES


def test_fetch_follows_redirects(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/old/puzzle24.png").respond_with_response(
        Response(status=302, headers={"Location": httpserver.url_for("/new/puzzle24.png")})
    )
    httpserver.expect_request("/new/puzzle24.png").respond_with_data(IMAGE_BYTES)

    assert fetcher.fetch(httpserver.url_for("/old/puzzle24.png"), MAX_BYTES).content == IMAGE_BYTES


def test_fetch_accepts_an_image_of_exactly_the_maximum_size(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/puzzle24.jpg").respond_with_data(b"x" * 100)

    assert len(fetcher.fetch(httpserver.url_for("/puzzle24.jpg"), 100).content) == 100


def test_fetch_stops_reading_one_byte_over_the_maximum_size(fetcher, httpserver: HTTPServer):
    httpserver.expect_request("/puzzle24.jpg").respond_with_data(b"x" * 500)

    assert len(fetcher.fetch(httpserver.url_for("/puzzle24.jpg"), 100).content) == 101


def test_fetch_reads_a_body_without_a_declared_length(fetcher, httpserver: HTTPServer):
    def stream(_request):
        return Response((b"x" * 60 for _ in range(3)), headers={"Content-Type": "image/jpeg"})

    httpserver.expect_request("/puzzle24.jpg").respond_with_handler(stream)

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


def test_fetch_raises_error_when_the_download_takes_too_long(httpserver: HTTPServer):
    times = iter([0.0, 11.0])
    fetcher = WebImageFetcher(timeout_seconds=10, is_allowed=allow_any_address, monotonic=lambda: next(times))
    httpserver.expect_request("/puzzle24.jpg").respond_with_data(IMAGE_BYTES)
    url = httpserver.url_for("/puzzle24.jpg")

    with pytest.raises(ImageError, match="Timed out downloading image"):
        fetcher.fetch(url, MAX_BYTES)


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/puzzle24.jpg", "puzzle24.jpg"])
def test_fetch_raises_error_for_unsupported_scheme(fetcher, url):
    with pytest.raises(ImageError, match="Unsupported image URL scheme"):
        fetcher.fetch(url, MAX_BYTES)


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "localhost", "[::1]", "169.254.169.254", "10.0.0.1", "192.168.1.1", "[::ffff:127.0.0.1]"],
)
def test_fetch_refuses_non_public_addresses_by_default(host):
    default_policy_fetcher = WebImageFetcher(timeout_seconds=2)
    url = f"http://{host}:9/puzzle24.jpg"

    with pytest.raises(ImageError, match="Image URL does not point to a public address"):
        default_policy_fetcher.fetch(url, MAX_BYTES)


def test_fetch_refuses_a_redirect_to_a_non_public_address(httpserver: HTTPServer):
    seen = []

    def allow_first_address_only(address) -> bool:
        seen.append(address)
        return len(seen) == 1

    httpserver.expect_request("/start.jpg").respond_with_response(
        Response(status=302, headers={"Location": "http://localhost:9/internal.jpg"})
    )
    fetcher = WebImageFetcher(is_allowed=allow_first_address_only)
    url = httpserver.url_for("/start.jpg")

    with pytest.raises(ImageError, match="Image URL does not point to a public address"):
        fetcher.fetch(url, MAX_BYTES)
