import logging
import time
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from crossword_solver_domain_use_case.image import Image
from crossword_solver_domain_use_case.image_downloader import ImageDownloader
from PIL import Image as PILImage

from .hash_factory import HashFactory
from .image_converter import ImageConverter
from .image_error import ImageError
from .image_rotator import ImageRotator
from .url_converter import UrlConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DefaultImageDownloader(ImageDownloader):
    def __init__(
        self,
        rotator: ImageRotator | None = None,
        image_converter: ImageConverter | None = None,
        url_converter: UrlConverter | None = None,
        hash_factory: HashFactory | None = None,
    ):
        self.rotator = rotator or ImageRotator()
        self.image_converter = image_converter or ImageConverter()
        self.url_converter = url_converter or UrlConverter()
        self.hash_factory = hash_factory or HashFactory()

    def download_image(self, image_url: str) -> Image:
        start = time.perf_counter()
        image = self._get_image(image_url)
        logger.info(
            "Downloaded image in %.2f seconds",
            time.perf_counter() - start,
        )

        start = time.perf_counter()
        image_bytes = self.image_converter.to_bytes(image)
        logger.info(
            "Converted image to bytes in %.2f seconds",
            time.perf_counter() - start,
        )

        return Image(
            name=self.url_converter.to_filename_excluding_extension(image_url),
            format=self.url_converter.to_extension(image_url),
            image=image,
            bytes=image_bytes,
            hash=self.hash_factory.to_hash(image_bytes),
        )

    def _get_image(self, image_url: str) -> PILImage.Image:
        start = time.perf_counter()
        try:
            with urlopen(image_url) as response:
                downloaded_bytes = response.read()

            logger.info(
                "Downloaded image from URL in %.2f seconds",
                time.perf_counter() - start,
            )

            start = time.perf_counter()
            image = PILImage.open(BytesIO(downloaded_bytes))
            image.load()
            logger.info(
                "Decoded image in %.2f seconds",
                time.perf_counter() - start,
            )
            return self.rotator.rotate_if_required(image)
        except (HTTPError, URLError) as e:
            raise ImageError(f"Failed to download image from {image_url}") from e
