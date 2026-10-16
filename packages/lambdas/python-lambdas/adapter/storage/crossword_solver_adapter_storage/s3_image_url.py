from urllib.parse import urlparse

from crossword_solver_domain_use_case.image_error import ImageError

SCHEME = "s3"


def to_s3_url(bucket: str, key: str) -> str:
    return f"{SCHEME}://{bucket}/{key}"


def parse_s3_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    key = parsed.path.lstrip("/")
    if parsed.scheme != SCHEME or not parsed.netloc or not key:
        raise ImageError("Invalid S3 image URL")
    return parsed.netloc, key
