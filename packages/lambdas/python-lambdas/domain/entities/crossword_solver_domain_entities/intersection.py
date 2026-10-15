from dataclasses import dataclass
from typing import TYPE_CHECKING

from .coordinates import Coordinates
from .direction import Direction
from .id import Id

if TYPE_CHECKING:
    from .word import Word


@dataclass(frozen=True)
class IntersectingWord:
    word: Word
    index: int

    @property
    def id(self) -> Id:
        return self.word.id

    def has_same_id(self, other: Word) -> bool:
        return self.has_id(other.id)

    def has_id(self, word_id: Id) -> bool:
        return self.word.id == word_id


@dataclass(frozen=True)
class Intersection:
    across: IntersectingWord
    down: IntersectingWord

    @classmethod
    def of(cls, across: Word, down: Word, coordinates: Coordinates) -> Intersection:
        return cls(
            IntersectingWord(across, coordinates.x - across.x),
            IntersectingWord(down, down.y - coordinates.y),
        )

    @property
    def across_index(self) -> int:
        return self.across.index

    @property
    def down_index(self) -> int:
        return self.down.index

    def to_index(self, direction: Direction) -> int:
        return self.across_index if direction == Direction.ACROSS else self.down_index

    def to_intersecting_index(self, direction: Direction) -> int:
        return self.down_index if direction == Direction.ACROSS else self.across_index

    def to_intersecting_id(self, word_id: Id) -> Id:
        return self.down.id if self.across.has_id(word_id) else self.across.id

    def to_intersecting_id_for_direction(self, direction: Direction) -> Id:
        return self.down.id if direction == Direction.ACROSS else self.across.id

    def get_other_word(self, word: Word) -> Word:
        return self.down.word if self.across.has_same_id(word) else self.across.word

    def contains(self, word: Word) -> bool:
        return self.across.has_same_id(word) or self.down.has_same_id(word)

    def contains_id(self, word_id: Id) -> bool:
        return self.across.has_id(word_id) or self.down.has_id(word_id)
