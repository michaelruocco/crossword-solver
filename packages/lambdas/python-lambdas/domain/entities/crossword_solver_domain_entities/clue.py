from dataclasses import dataclass

from .clue_type import ClueType
from .hyphen_normalizer import normalize_hyphens
from .id import Id


@dataclass(frozen=True)
class Clue:
    id: Id
    text: str
    lengths: list[int]
    type: ClueType | None = None

    @property
    def numeric_id(self) -> int:
        return self.id.number

    @property
    def direction(self):
        return self.id.direction

    @property
    def total_length(self) -> int:
        return sum(self.lengths)

    def normalize_hyphens(self) -> Clue:
        return Clue(
            id=self.id,
            text=normalize_hyphens(self.text),
            lengths=self.lengths,
            type=self.type,
        )

    def with_type(self, clue_type: ClueType) -> Clue:
        return Clue(
            id=self.id,
            text=self.text,
            lengths=self.lengths,
            type=clue_type,
        )
