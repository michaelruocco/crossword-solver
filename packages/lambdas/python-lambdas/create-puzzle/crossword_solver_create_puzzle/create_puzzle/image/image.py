from dataclasses import dataclass

from PIL import Image as PILImage


@dataclass
class Image:
    name: str
    format: str
    image: PILImage.Image
    bytes: bytes
    hash: str