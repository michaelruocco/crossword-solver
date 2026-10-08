from enum import Enum


class Direction(Enum):
    ACROSS = "A"
    DOWN = "D"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls.__members__.get(value.upper())
        return None
