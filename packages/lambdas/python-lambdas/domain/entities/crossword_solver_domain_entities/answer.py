from dataclasses import dataclass

from .id import Id


@dataclass(frozen=True)
class Answer:
    id: Id
    value: str
