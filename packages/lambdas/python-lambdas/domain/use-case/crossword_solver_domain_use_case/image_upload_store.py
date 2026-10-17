from typing import Protocol
from uuid import UUID

from .image_upload import ImageUpload


class ImageUploadStore(Protocol):
    def create_upload(self, import_id: UUID, filename: str, max_size_in_bytes: int) -> ImageUpload: ...
