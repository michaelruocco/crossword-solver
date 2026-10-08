from typing import Protocol

from .image import Image


class ImageDownloader(Protocol):
    def download_image(self, image_url: str) -> Image: ...
