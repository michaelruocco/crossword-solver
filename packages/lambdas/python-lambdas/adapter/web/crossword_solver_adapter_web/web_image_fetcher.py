import http.client
import ipaddress
import socket
import ssl
import time
import urllib.request
from collections.abc import Callable
from pathlib import PurePosixPath
from urllib.parse import urlparse

from crossword_solver_domain_use_case.address_policy import IpAddress, is_public_address
from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_domain_use_case.image_fetcher import ImageFetcher
from crossword_solver_domain_use_case.image_file import ImageFile

AddressPolicy = Callable[[IpAddress], bool]

CHUNK_BYTES = 64 * 1024


def _connect_to_allowed_address(host: str, port: int, timeout: float, is_allowed: AddressPolicy) -> socket.socket:
    candidates = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not candidates or not all(is_allowed(ipaddress.ip_address(candidate[4][0])) for candidate in candidates):
        raise ImageError("Image URL does not point to a public address")

    last_error: OSError | None = None
    for family, socket_type, protocol, _, address in candidates:
        candidate = socket.socket(family, socket_type, protocol)
        try:
            candidate.settimeout(timeout)
            candidate.connect(address)
            return candidate
        except OSError as e:
            candidate.close()
            last_error = e
    raise last_error or OSError("Could not connect")


# The address is checked at connect time, so it also covers redirects and DNS answers that change between lookups.
class _AllowedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, *args, is_allowed: AddressPolicy, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = lambda address, timeout, source_address=None: _connect_to_allowed_address(
            address[0], address[1], timeout, is_allowed
        )


class _AllowedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, *args, is_allowed: AddressPolicy, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = lambda address, timeout, source_address=None: _connect_to_allowed_address(
            address[0], address[1], timeout, is_allowed
        )


class _AllowedHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, is_allowed: AddressPolicy):
        super().__init__()
        self.is_allowed = is_allowed

    def http_open(self, req):
        return self.do_open(_AllowedHTTPConnection, req, is_allowed=self.is_allowed)


class _AllowedHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, is_allowed: AddressPolicy):
        self.context = ssl.create_default_context()
        super().__init__(context=self.context)
        self.is_allowed = is_allowed

    def https_open(self, req):
        return self.do_open(_AllowedHTTPSConnection, req, context=self.context, is_allowed=self.is_allowed)


class WebImageFetcher(ImageFetcher):
    TIMEOUT_SECONDS = 10

    def __init__(
        self,
        timeout_seconds: float = TIMEOUT_SECONDS,
        is_allowed: AddressPolicy = is_public_address,
        monotonic: Callable[[], float] = time.monotonic,
    ):
        self.timeout_seconds = timeout_seconds
        self.monotonic = monotonic
        # Only web handlers are added, so a redirect cannot lead to file or ftp URLs.
        self.opener = urllib.request.OpenerDirector()
        for handler in (
            urllib.request.UnknownHandler(),
            _AllowedHTTPHandler(is_allowed),
            _AllowedHTTPSHandler(is_allowed),
            urllib.request.HTTPDefaultErrorHandler(),
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPErrorProcessor(),
        ):
            self.opener.add_handler(handler)

    def fetch(self, image_url: str, max_bytes: int) -> ImageFile:
        if urlparse(image_url).scheme.lower() not in ("http", "https"):
            raise ImageError("Unsupported image URL scheme")

        content = self._download(image_url, max_bytes)
        return ImageFile(filename=PurePosixPath(urlparse(image_url).path).name, content=content)

    def _download(self, image_url: str, max_bytes: int) -> bytes:
        deadline = self.monotonic() + self.timeout_seconds
        chunks: list[bytes] = []
        total = 0
        try:
            with self.opener.open(urllib.request.Request(image_url), timeout=self.timeout_seconds) as response:
                # One byte more than the limit is enough for the caller to see the image is too large.
                while total <= max_bytes:
                    chunk = response.read(min(CHUNK_BYTES, max_bytes + 1 - total))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total += len(chunk)
                    if self.monotonic() > deadline:
                        raise ImageError("Timed out downloading image")
        except (OSError, http.client.HTTPException) as e:
            raise ImageError("Failed to download image") from e
        return b"".join(chunks)
