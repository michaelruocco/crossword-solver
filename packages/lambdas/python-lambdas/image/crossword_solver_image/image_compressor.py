from io import BytesIO

from PIL import Image


class ImageCompressor:
    DEFAULT_MAX_SIZE_BYTES = 4 * 1024 * 1024
    DEFAULT_QUALITY = 0.8
    DEFAULT_MIN_SIZE = 100
    DEFAULT_TARGET_FORMAT = "JPEG"

    def __init__(
        self,
        max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES,
        initial_quality: float = DEFAULT_QUALITY,
        min_width: int = DEFAULT_MIN_SIZE,
        min_height: int = DEFAULT_MIN_SIZE,
        target_format: str = DEFAULT_TARGET_FORMAT,
    ):
        self.max_size_bytes = max_size_bytes
        self.initial_quality = initial_quality
        self.min_width = min_width
        self.min_height = min_height
        self.target_format = target_format

    def compress_and_resize(self, image: Image.Image) -> bytes:
        rgb_image = self._to_rgb(image)
        width, height = image.size
        quality = self.initial_quality

        image_data = self._compress_to_bytes(rgb_image, quality)

        while len(image_data) > self.max_size_bytes and (width > self.min_width or height > self.min_height):
            width = int(width * 0.9)
            height = int(height * 0.9)

            rgb_image = self._resize(image, width, height)
            image_data = self._compress_to_bytes(rgb_image, quality)

        return image_data

    def _compress_to_bytes(
        self,
        image: Image.Image,
        quality: float,
    ) -> bytes:
        output = BytesIO()

        image.save(
            output,
            format=self.target_format,
            quality=round(quality * 100),
        )

        return output.getvalue()

    @staticmethod
    def _to_rgb(image: Image.Image) -> Image.Image:
        if image.mode == "RGB":
            return image

        rgb_image = Image.new("RGB", image.size, "white")
        rgb_image.paste(
            image,
            mask=image.getchannel("A") if "A" in image.getbands() else None,
        )
        return rgb_image

    @staticmethod
    def _resize(
        original_image: Image.Image,
        width: int,
        height: int,
    ) -> Image.Image:
        return original_image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )
