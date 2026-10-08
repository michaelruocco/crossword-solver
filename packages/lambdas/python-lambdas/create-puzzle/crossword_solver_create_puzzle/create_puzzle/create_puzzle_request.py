from pydantic import BaseModel, Field


class CreatePuzzleRequest(BaseModel):
    image_url: str = Field(alias="imageUrl")
