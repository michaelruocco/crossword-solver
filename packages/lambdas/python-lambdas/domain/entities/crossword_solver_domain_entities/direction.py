from enum import Enum


class Direction(Enum):
    ACROSS = "A"
    DOWN = "D"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str) and value.upper() in cls.__members__:
            return cls.__members__[value.upper()]
        raise ValueError(f"{value!r} is not a valid Direction, expected one of: A, D, ACROSS, DOWN")
