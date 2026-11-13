from dataclasses import dataclass

from .id import Id
from .intersection import Intersection


@dataclass(frozen=True)
class Answer:
    id: Id
    value: str

    @property
    def normalized_value(self) -> str:
        return "".join(self.value.split()).upper()

    def conflicts_with(self, other: Answer, intersection: Intersection) -> bool:
        answer_index = intersection.to_index(self.id.direction)
        other_index = intersection.to_intersecting_index(self.id.direction)
        return (
            self.normalized_value[answer_index : answer_index + 1]
            != other.normalized_value[other_index : other_index + 1]
        )
