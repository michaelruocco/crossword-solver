from collections.abc import Collection, Iterator

from .clue import Clue
from .clue_type import ClueType
from .direction import Direction
from .id import Id


class Clues:
    def __init__(self, values: Collection[Clue]):
        self._values: dict[Id, Clue] = {
            clue.id: clue for clue in values
        }

    def __iter__(self) -> Iterator[Clue]:
        return iter(self._values.values())

    def __len__(self) -> int:
        return len(self._values)

    def find(self, clue_id: Id) -> Clue | None:
        return self._values.get(clue_id)

    def has_clue(self, clue_id: Id) -> bool:
        return clue_id in self._values

    def get_across(self) -> "Clues":
        return self._of_direction(Direction.ACROSS)

    def get_down(self) -> "Clues":
        return self._of_direction(Direction.DOWN)

    def with_type(self, clue_type: ClueType) -> "Clues":
        return Clues(
            [clue.with_type(clue_type) for clue in self]
        )

    def normalize_text_hyphens(self) -> "Clues":
        return Clues(
            [clue.normalize_hyphens() for clue in self]
        )

    def _of_direction(self, direction: Direction) -> "Clues":
        return Clues(
            [clue for clue in self if clue.direction == direction]
        )