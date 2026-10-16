import http.client
import urllib.request
from pathlib import PurePosixPath
from urllib.error import URLError
from urllib.parse import urlparse

from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_domain_use_case.image_fetcher import ImageFetcher
from crossword_solver_domain_use_case.image_file import ImageFile


class WebImageFetcher(ImageFetcher):
    TIMEOUT_SECONDS = 10

    def __init__(self, timeout_seconds: float = TIMEOUT_SECONDS):
        self.timeout_seconds = timeout_seconds

    def fetch(self, image_url: str, max_bytes: int) -> ImageFile:
        # urlopen also reads file: URLs, which must never be fetched.
        if urlparse(image_url).scheme.lower() not in ("http", "https"):
            raise ImageError("Unsupported image URL scheme")

        try:
            with urllib.request.urlopen(image_url, timeout=self.timeout_seconds) as response:
                # One byte more than the limit is enough for the caller to see the image is too large.
                content = response.read(max_bytes + 1)
        except (URLError, OSError, http.client.HTTPException) as e:
            raise ImageError("Failed to download image") from e

        return ImageFile(filename=PurePosixPath(urlparse(image_url).path).name, content=content)
