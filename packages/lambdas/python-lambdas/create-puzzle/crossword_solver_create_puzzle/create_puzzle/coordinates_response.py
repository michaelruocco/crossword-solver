from crossword_solver_domain_entities.coordinates import Coordinates
from pydantic import BaseModel


class CoordinatesResponse(BaseModel):
    x: int
    y: int

    @classmethod
    def from_coordinates(cls, coordinates: Coordinates) -> CoordinatesResponse:
        return cls(x=coordinates.x, y=coordinates.y)
