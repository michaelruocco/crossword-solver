from typing import Protocol

from .image_file import ImageFile


class ImageStore(Protocol):
    def save(self, file: ImageFile) -> str: ...
