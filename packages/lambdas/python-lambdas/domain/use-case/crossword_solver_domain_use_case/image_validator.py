from collections.abc import Collection

from crossword_solver_domain_entities.image_file import ImageFile

from .image import Image
from .invalid_image_error import InvalidImageError

BYTES_PER_MB = 1024 * 1024


class ImageValidator:
    DEFAULT_MAX_SIZE_IN_MB = 20
    DEFAULT_ALLOWED_FORMATS = ("png", "jpg", "jpeg", "webp")

    def __init__(
        self,
        max_size_in_mb: int = DEFAULT_MAX_SIZE_IN_MB,
        allowed_formats: Collection[str] = DEFAULT_ALLOWED_FORMATS,
    ):
        self.max_size_in_mb = max_size_in_mb
        self.allowed_formats = [allowed_format.lower() for allowed_format in allowed_formats]

    @property
    def max_size_in_bytes(self) -> int:
        return self.max_size_in_mb * BYTES_PER_MB

    def validate(self, image: Image) -> None:
        self._validate(image.name, image.format, len(image.bytes))

    def validate_file(self, file: ImageFile) -> None:
        self._validate(file.name, file.format, len(file.content))

    # For uploads, where the size is enforced by the upload itself.
    def validate_filename(self, filename: str) -> None:
        file = ImageFile(filename, b"")
        self._validate_name_and_format(file.name, file.format)

    def _validate(self, name: str, image_format: str, size_in_bytes: int) -> None:
        self._validate_name_and_format(name, image_format)

        if size_in_bytes == 0:
            raise InvalidImageError("image file is empty")

        # No measured size, because a fetcher may stop reading once the limit is passed.
        if size_in_bytes > self.max_size_in_bytes:
            raise InvalidImageError(f"image file is larger than max allowed file size {self.max_size_in_mb} MB")

    def _validate_name_and_format(self, name: str, image_format: str) -> None:
        if not name:
            raise InvalidImageError("file name is mandatory")

        normalised_format = image_format.lstrip(".").lower()
        if normalised_format not in self.allowed_formats:
            raise InvalidImageError(
                f"image format {normalised_format} is not an allowed format {','.join(self.allowed_formats)}"
            )
