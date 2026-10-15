from collections.abc import Collection, Iterator
from itertools import combinations

from .id import Id
from .intersection import Intersection
from .word import Word
from .word_not_found_for_id_error import WordNotFoundForIdError


class Words:
    def __init__(self, values: Collection[Word], intersections: Collection[Intersection] | None = None):
        self._values = list(values)
        self._intersections = list(intersections) if intersections is not None else _build_intersections(self._values)

    def __iter__(self) -> Iterator[Word]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Words):
            return NotImplemented
        return self._values == other._values and set(self._intersections) == set(other._intersections)

    def __repr__(self) -> str:
        return f"Words(values={self._values!r}, intersections={self._intersections!r})"

    def find_by_id(self, word_id: Id) -> Word:
        for word in self._values:
            if word.has_id(word_id):
                return word
        raise WordNotFoundForIdError(word_id)

    def get_intersecting_ids(self, word_id: Id) -> list[Id]:
        return [word.id for word in self.get_intersecting_words(self.find_by_id(word_id))]

    def get_intersecting_words(self, word: Word) -> list[Word]:
        return [intersection.get_other_word(word) for intersection in self.get_intersections(word)]

    def get_intersections(self, word: Word) -> list[Intersection]:
        return [intersection for intersection in self._intersections if intersection.contains(word)]

    def get_intersections_by_id(self, word_id: Id) -> list[Intersection]:
        return [intersection for intersection in self._intersections if intersection.contains_id(word_id)]


def _build_intersections(values: list[Word]) -> list[Intersection]:
    intersections = (first.find_intersection_between(second) for first, second in combinations(values, 2))
    return [intersection for intersection in intersections if intersection is not None]
