from dataclasses import dataclass

from PIL import Image as PILImage


@dataclass
class Image:
    name: str
    format: str
    pil_image: PILImage.Image
    bytes: bytes
    hash: str
