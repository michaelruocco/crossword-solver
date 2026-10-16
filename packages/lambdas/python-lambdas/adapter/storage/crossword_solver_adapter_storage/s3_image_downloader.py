import boto3
from botocore.exceptions import BotoCoreError, ClientError
from crossword_solver_domain_use_case.image import Image
from crossword_solver_domain_use_case.image_downloader import ImageDownloader
from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_image.image_factory import ImageFactory

from .s3_image_url import parse_s3_url


class S3ImageDownloader(ImageDownloader):
    def __init__(self, bucket: str, client=None, image_factory: ImageFactory | None = None):
        self.bucket = bucket
        self.client = client or boto3.client("s3")
        self.image_factory = image_factory or ImageFactory()

    def download_image(self, image_url: str) -> Image:
        bucket, key = parse_s3_url(image_url)
        # Only the configured bucket is read, whatever bucket the URL names.
        if bucket != self.bucket:
            raise ImageError("Image is not in the images bucket")

        try:
            image_bytes = self.client.get_object(Bucket=bucket, Key=key)["Body"].read()
        except (BotoCoreError, ClientError) as e:
            raise ImageError("Failed to read image") from e

        return self.image_factory.to_image(image_url, image_bytes)
