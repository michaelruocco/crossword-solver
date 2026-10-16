import mimetypes
import re
from pathlib import PurePosixPath
from uuid import uuid4

import boto3
from crossword_solver_domain_use_case.image_file import ImageFile
from crossword_solver_domain_use_case.image_store import ImageStore

from .s3_image_url import to_s3_url

MAX_FILENAME_LENGTH = 100


class S3ImageStore(ImageStore):
    KEY_PREFIX = "images"

    def __init__(self, bucket: str, client=None):
        self.bucket = bucket
        self.client = client or boto3.client("s3")

    def save(self, file: ImageFile) -> str:
        safe_filename = _to_safe_filename(file.filename)
        # The unique folder stops files with the same name overwriting each other.
        key = f"{self.KEY_PREFIX}/{uuid4()}/{safe_filename}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file.content,
            ContentType=mimetypes.guess_type(safe_filename)[0] or "application/octet-stream",
        )
        return to_s3_url(self.bucket, key)


def _to_safe_filename(filename: str) -> str:
    name = PurePosixPath(filename.replace("\\", "/")).name
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)[-MAX_FILENAME_LENGTH:]
    return safe if safe.strip("._") else "image"
