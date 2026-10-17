import mimetypes
import re
from pathlib import PurePosixPath
from urllib.parse import unquote_plus
from uuid import UUID, uuid4

import boto3
from crossword_solver_domain_entities.image_file import ImageFile
from crossword_solver_domain_use_case.image_store import ImageStore
from crossword_solver_domain_use_case.image_upload import ImageUpload
from crossword_solver_domain_use_case.image_upload_store import ImageUploadStore

from .s3_image_url import to_s3_url

MAX_FILENAME_LENGTH = 100
UPLOAD_KEY_PREFIX = "uploads"


class S3ImageStore(ImageStore, ImageUploadStore):
    KEY_PREFIX = "images"
    DEFAULT_UPLOAD_EXPIRY_SECONDS = 300

    def __init__(self, bucket: str, client=None, upload_expiry_seconds: int = DEFAULT_UPLOAD_EXPIRY_SECONDS):
        self.bucket = bucket
        self.client = client or boto3.client("s3")
        self.upload_expiry_seconds = upload_expiry_seconds

    def save(self, file: ImageFile) -> str:
        safe_filename = _to_safe_filename(file.filename)
        # The unique folder stops files with the same name overwriting each other.
        key = f"{self.KEY_PREFIX}/{uuid4()}/{safe_filename}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file.content,
            ContentType=_to_content_type(safe_filename),
        )
        return to_s3_url(self.bucket, key)

    def create_upload(self, import_id: UUID, filename: str, max_size_in_bytes: int) -> ImageUpload:
        safe_filename = _to_safe_filename(filename)
        # The import id in the key is how the upload notification finds its import.
        key = f"{UPLOAD_KEY_PREFIX}/{import_id}/{safe_filename}"
        content_type = _to_content_type(safe_filename)
        post = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[{"Content-Type": content_type}, ["content-length-range", 1, max_size_in_bytes]],
            ExpiresIn=self.upload_expiry_seconds,
        )
        return ImageUpload(image_url=to_s3_url(self.bucket, key), url=post["url"], fields=post["fields"])


def import_id_from_upload_key(key: str) -> UUID:
    # Keys in S3 notifications are URL encoded.
    parts = unquote_plus(key).split("/")
    if len(parts) != 3 or parts[0] != UPLOAD_KEY_PREFIX:
        raise ValueError("Not an upload key")
    return UUID(parts[1])


def _to_safe_filename(filename: str) -> str:
    name = PurePosixPath(filename.replace("\\", "/")).name
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)[-MAX_FILENAME_LENGTH:]
    return safe if safe.strip("._") else "image"


def _to_content_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"
