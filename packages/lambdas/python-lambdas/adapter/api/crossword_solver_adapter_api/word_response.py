from crossword_solver_domain_entities.word import Word
from pydantic import BaseModel

from .coordinates_response import CoordinatesResponse


class WordResponse(BaseModel):
    id: int
    direction: str
    length: int
    coordinates: CoordinatesResponse

    @classmethod
    def from_word(cls, word: Word) -> WordResponse:
        return cls(
            id=word.numeric_id,
            direction=word.direction.name,
            length=word.length,
            coordinates=CoordinatesResponse.from_coordinates(word.coordinates),
        )
