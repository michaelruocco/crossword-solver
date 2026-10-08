from pydantic import BaseModel

from .direction import Direction
from .clue import Clue
from .id import Id


class BedrockClue(BaseModel):
    id: int
    text: str
    direction: Direction
    lengths: list[int]

    def to_clue(self) -> Clue:
        return Clue(
            id=(
                Id.across(self.id)
                if self.direction == Direction.ACROSS
                else Id.down(self.id)
            ),
            text=self.text,
            lengths=self.lengths,
        )