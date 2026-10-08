from typing import Protocol

from crossword_solver_domain_entities.clues import Clues

from .image import Image


class ClueExtractor(Protocol):
    def extract_clues(self, image: Image) -> Clues: ...
