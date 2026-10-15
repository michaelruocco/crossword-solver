from uuid import UUID

from pydantic import BaseModel, Field


class PuzzleImportMessage(BaseModel):
    import_id: UUID = Field(alias="importId")
