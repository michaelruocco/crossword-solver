import logging
import time
from io import BytesIO

from crossword_solver_domain_use_case.image import Image
from crossword_solver_domain_use_case.image_error import ImageError
from PIL import Image as PILImage
from PIL import UnidentifiedImageError

from .hash_factory import HashFactory
from .image_rotator import ImageRotator
from .url_converter import UrlConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ImageFactory:
    def __init__(
        self,
        rotator: ImageRotator | None = None,
        url_converter: UrlConverter | None = None,
        hash_factory: HashFactory | None = None,
    ):
        self.rotator = rotator or ImageRotator()
        self.url_converter = url_converter or UrlConverter()
        self.hash_factory = hash_factory or HashFactory()

    def to_image(self, image_url: str, image_bytes: bytes) -> Image:
        start = time.perf_counter()
        try:
            image = PILImage.open(BytesIO(image_bytes))
            image.load()
        except UnidentifiedImageError as e:
            raise ImageError("Failed to decode image") from e
        logger.info(
            "Decoded image in %.2f seconds",
            time.perf_counter() - start,
        )

        return Image(
            name=self.url_converter.to_filename_excluding_extension(image_url),
            format=self.url_converter.to_extension(image_url),
            pil_image=self.rotator.rotate_if_required(image),
            bytes=image_bytes,
            hash=self.hash_factory.to_hash(image_bytes),
        )
