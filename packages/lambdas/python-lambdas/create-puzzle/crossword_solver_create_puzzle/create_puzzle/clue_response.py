from crossword_solver_domain_entities.clue import Clue
from pydantic import BaseModel


class ClueResponse(BaseModel):
    id: int
    direction: str
    text: str
    lengths: list[int]

    @classmethod
    def from_clue(cls, clue: Clue) -> ClueResponse:
        return cls(
            id=clue.numeric_id,
            direction=clue.direction.name,
            text=clue.text,
            lengths=clue.lengths,
        )
