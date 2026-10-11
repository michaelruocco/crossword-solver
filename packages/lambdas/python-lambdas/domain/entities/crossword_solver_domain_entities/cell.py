from dataclasses import dataclass

from .coordinates import Coordinates


@dataclass(frozen=True)
class Cell:
    coordinates: Coordinates
    black: bool
    id: int | None = None
    letter: str | None = None
