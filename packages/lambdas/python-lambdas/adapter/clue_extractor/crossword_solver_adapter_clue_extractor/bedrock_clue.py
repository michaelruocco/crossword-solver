from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id
from pydantic import BaseModel


class BedrockClue(BaseModel):
    id: int
    text: str
    direction: Direction
    lengths: list[int]

    def to_clue(self) -> Clue:
        return Clue(
            id=(Id.across(self.id) if self.direction == Direction.ACROSS else Id.down(self.id)),
            text=self.text,
            lengths=self.lengths,
        )
