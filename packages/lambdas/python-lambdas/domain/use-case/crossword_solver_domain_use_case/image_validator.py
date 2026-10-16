from collections.abc import Collection

from .image import Image
from .invalid_image_error import InvalidImageError

BYTES_PER_MB = 1024 * 1024


class ImageValidator:
    DEFAULT_MAX_SIZE_IN_MB = 20
    DEFAULT_ALLOWED_FORMATS = ("png", "jpg", "jpeg")

    def __init__(
        self,
        max_size_in_mb: int = DEFAULT_MAX_SIZE_IN_MB,
        allowed_formats: Collection[str] = DEFAULT_ALLOWED_FORMATS,
    ):
        self.max_size_in_mb = max_size_in_mb
        self.allowed_formats = [allowed_format.lower() for allowed_format in allowed_formats]

    def validate(self, image: Image) -> None:
        if not image.name:
            raise InvalidImageError("file name is mandatory")

        image_format = image.format.lstrip(".").lower()
        if image_format not in self.allowed_formats:
            raise InvalidImageError(
                f"image format {image_format} is not an allowed format {','.join(self.allowed_formats)}"
            )

        if not image.bytes:
            raise InvalidImageError("image file is empty")

        size_in_mb = len(image.bytes) / BYTES_PER_MB
        if size_in_mb > self.max_size_in_mb:
            raise InvalidImageError(
                f"image file size {size_in_mb:.2f} MB is larger than max allowed file size {self.max_size_in_mb} MB"
            )
