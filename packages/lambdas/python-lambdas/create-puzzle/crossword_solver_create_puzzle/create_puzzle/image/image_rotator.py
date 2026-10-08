from PIL import Image, ImageOps


class ImageRotator:
    def rotate_if_required(self, image: Image.Image) -> Image.Image:
        return ImageOps.exif_transpose(image)
