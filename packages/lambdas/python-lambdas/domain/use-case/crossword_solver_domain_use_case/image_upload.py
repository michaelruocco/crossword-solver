from dataclasses import dataclass


@dataclass(frozen=True)
class ImageUpload:
    # Where the image will be read from once uploaded.
    image_url: str
    # The form the client posts the file to.
    url: str
    fields: dict[str, str]
