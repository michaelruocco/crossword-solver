from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .direction import Direction
from .id import Id
from .intersection import Intersection

if TYPE_CHECKING:
    from .clue import Clue


@dataclass(frozen=True)
class Answer:
    id: Id
    value: str
    confidence_score: int = 0

    @classmethod
    def no_match(cls, clue_or_id: Clue | Id) -> Answer:
        answer_id = clue_or_id.id if not isinstance(clue_or_id, Id) else clue_or_id
        return cls(id=answer_id, value="NO_MATCH", confidence_score=0)

    @property
    def normalized_value(self) -> str:
        return "".join(self.value.split()).upper()

    def with_id(self, answer_id: Id) -> Answer:
        return Answer(
            id=answer_id,
            value=self.value,
            confidence_score=self.confidence_score,
        )

    def with_value(self, value: str) -> Answer:
        return Answer(
            id=self.id,
            value=value,
            confidence_score=self.confidence_score,
        )

    @property
    def numeric_id(self) -> int:
        return self.id.number

    @property
    def direction(self) -> Direction:
        return self.id.direction

    def has_same_value(self, other: Answer) -> bool:
        return self.value == other.value

    def has_direction(self, direction: Direction) -> bool:
        return self.id.direction == direction

    def letter_at(self, index: int) -> str | None:
        return self.value[index] if 0 <= index < len(self.value) else None

    def matches(self, pattern: str) -> bool:
        return all(
            not character.isalpha() or (index < len(self.value) and self.value[index] == character)
            for index, character in enumerate(pattern)
        )

    @property
    def id_as_string(self) -> str:
        return str(self.id)

    def as_string(self) -> str:
        return f"{self.id} {self.value} {self.confidence_score}"

    def conflicts_with(self, other: Answer, intersection: Intersection) -> bool:
        answer_index = intersection.to_index(self.id.direction)
        other_index = intersection.to_intersecting_index(self.id.direction)
        answer_letter = self.normalized_value[answer_index : answer_index + 1]
        other_letter = other.normalized_value[other_index : other_index + 1]
        return answer_letter != other_letter
