from io import BytesIO

from PIL import Image


class ImageConverter:
    def to_rgb(self, image: Image.Image) -> Image.Image:
        if image.mode == "RGB":
            return image

        rgb_image = Image.new("RGB", image.size, "white")
        rgb_image.paste(image, mask=image.getchannel("A") if "A" in image.getbands() else None)

        return rgb_image

    def to_bytes(self, image: Image.Image) -> bytes:
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
