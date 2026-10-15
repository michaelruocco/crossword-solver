from dataclasses import dataclass

from .coordinates import Coordinates
from .direction import Direction
from .id import Id
from .intersection import Intersection


@dataclass(frozen=True)
class Word:
    id: Id
    length: int
    coordinates: Coordinates

    @property
    def numeric_id(self) -> int:
        return self.id.number

    @property
    def x(self) -> int:
        return self.coordinates.x

    @property
    def y(self) -> int:
        return self.coordinates.y

    @property
    def direction(self) -> Direction:
        return self.id.direction

    def has_id(self, other_id: Id) -> bool:
        return self.id == other_id

    def has_same_id(self, other: Word) -> bool:
        return self.has_id(other.id)

    def find_intersection_between(self, other: Word) -> Intersection | None:
        coordinates = self._find_intersecting_coordinates(other)
        if coordinates is None:
            return None
        across, down = (self, other) if self.direction == Direction.ACROSS else (other, self)
        return Intersection.of(across, down, coordinates)

    def _all_coordinates(self) -> set[Coordinates]:
        # Across words run left to right, down words run top to bottom so y decreases.
        if self.direction == Direction.ACROSS:
            return {Coordinates(self.x + offset, self.y) for offset in range(self.length)}
        return {Coordinates(self.x, self.y - offset) for offset in range(self.length)}

    def _find_intersecting_coordinates(self, other: Word) -> Coordinates | None:
        if self.direction == other.direction:
            return None
        shared = self._all_coordinates() & other._all_coordinates()
        return next(iter(shared), None)
