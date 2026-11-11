from pydantic import BaseModel


class AnswerResponse(BaseModel):
    id: str
    value: str
