from dataclasses import dataclass

from crossword_solver_domain_entities.puzzle_import import PuzzleImport

from .image_upload import ImageUpload


@dataclass(frozen=True)
class PuzzleUpload:
    puzzle_import: PuzzleImport
    upload: ImageUpload
