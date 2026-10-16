from io import BytesIO

import boto3
import pytest
from crossword_solver_domain_use_case.image_error import ImageError
from moto import mock_aws
from PIL import Image as PILImage

from crossword_solver_adapter_storage.s3_image_downloader import S3ImageDownloader

BUCKET = "puzzle-images"
KEY = "images/abc/puzzle24.jpg"


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3", region_name="eu-west-2")
        client.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        yield client


@pytest.fixture
def downloader(s3) -> S3ImageDownloader:
    return S3ImageDownloader(BUCKET, client=s3)


@pytest.fixture
def jpeg_bytes() -> bytes:
    buffer = BytesIO()
    PILImage.new("RGB", (10, 10), "white").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_download_image_reads_and_decodes_the_object(downloader, s3, jpeg_bytes):
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=jpeg_bytes)

    image = downloader.download_image(f"s3://{BUCKET}/{KEY}")

    assert image.name == "puzzle24"
    assert image.format == ".jpg"
    assert image.pil_image.size == (10, 10)
    assert image.bytes == jpeg_bytes
    assert image.hash


def test_download_image_raises_error_when_the_object_is_missing(downloader):
    url = f"s3://{BUCKET}/images/missing/puzzle24.jpg"

    with pytest.raises(ImageError, match="Failed to read image"):
        downloader.download_image(url)


def test_download_image_raises_error_when_the_object_is_not_an_image(downloader, s3):
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=b"<html></html>")
    url = f"s3://{BUCKET}/{KEY}"

    with pytest.raises(ImageError, match="Failed to decode image"):
        downloader.download_image(url)


def test_download_image_raises_error_for_a_different_bucket(downloader):
    url = f"s3://another-bucket/{KEY}"

    with pytest.raises(ImageError, match="Image is not in the images bucket"):
        downloader.download_image(url)


def test_download_image_raises_error_for_a_url_that_is_not_s3(downloader):
    with pytest.raises(ImageError, match="Invalid S3 image URL"):
        downloader.download_image("https://example.com/puzzle.jpg")
