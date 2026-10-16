import pytest
from crossword_solver_domain_use_case.image_error import ImageError

from crossword_solver_adapter_storage.s3_image_url import parse_s3_url, to_s3_url


def test_to_s3_url():
    assert to_s3_url("my-bucket", "images/abc/puzzle.jpg") == "s3://my-bucket/images/abc/puzzle.jpg"


def test_parse_s3_url_returns_bucket_and_key():
    assert parse_s3_url("s3://my-bucket/images/abc/puzzle.jpg") == ("my-bucket", "images/abc/puzzle.jpg")


@pytest.mark.parametrize(
    "url",
    ["https://my-bucket/images/puzzle.jpg", "s3:///images/puzzle.jpg", "s3://my-bucket", "s3://my-bucket/", "nonsense"],
    ids=["wrong scheme", "no bucket", "no key", "empty key", "not a url"],
)
def test_parse_s3_url_raises_error_for_invalid_url(url):
    with pytest.raises(ImageError, match="Invalid S3 image URL"):
        parse_s3_url(url)
