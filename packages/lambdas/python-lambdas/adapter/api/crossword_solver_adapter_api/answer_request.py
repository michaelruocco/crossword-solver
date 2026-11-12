from pydantic import BaseModel


class AnswerRequest(BaseModel):
    id: str
    value: str
