from crossword_solver_domain_entities.clues import Clues

from .clue_extractor import ClueExtractor
from .clue_type_policy import ClueTypePolicy
from .image import Image


class CluesFactory:
    def __init__(self, clue_extractor: ClueExtractor, clue_type_policy: ClueTypePolicy):
        self.clue_extractor = clue_extractor
        self.clue_type_policy = clue_type_policy

    def build(self, image: Image) -> Clues:
        clues = self.clue_extractor.extract_clues(image)
        clue_type = self.clue_type_policy.determine_clue_type(clues)
        return clues.with_type(clue_type)
