from pydantic import BaseModel


class BedrockContent(BaseModel):
    type: str
    text: str


class BedrockResponse(BaseModel):
    content: list[BedrockContent]