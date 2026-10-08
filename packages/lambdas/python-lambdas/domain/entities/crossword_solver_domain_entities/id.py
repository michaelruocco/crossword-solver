from dataclasses import dataclass

from .direction import Direction


@dataclass(frozen=True)
class Id:
    number: int
    direction: Direction

    @classmethod
    def across(cls, number: int) -> Id:
        return cls(number, Direction.ACROSS)

    @classmethod
    def down(cls, number: int) -> Id:
        return cls(number, Direction.DOWN)

    def __str__(self) -> str:
        return f"{self.number}{self.direction.value}"
