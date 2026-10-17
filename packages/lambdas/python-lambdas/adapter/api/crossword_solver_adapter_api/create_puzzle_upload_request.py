from pydantic import BaseModel, Field


class CreatePuzzleUploadRequest(BaseModel):
    file_name: str = Field(alias="fileName", min_length=1, max_length=255)
