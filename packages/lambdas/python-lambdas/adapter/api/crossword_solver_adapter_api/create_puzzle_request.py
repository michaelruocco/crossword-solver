from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class CreatePuzzleRequest(BaseModel):
    image_url: str = Field(alias="imageUrl")

    @field_validator("image_url")
    @classmethod
    def _require_http_url(cls, value: str) -> str:
        # The image is downloaded with urlopen, which would also accept file: URLs.
        if urlparse(value).scheme not in ("http", "https"):
            raise ValueError("imageUrl must be an http or https URL")
        return value
