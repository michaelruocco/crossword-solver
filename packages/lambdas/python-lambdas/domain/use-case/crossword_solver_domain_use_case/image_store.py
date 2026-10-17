from typing import Protocol

from crossword_solver_domain_entities.image_file import ImageFile


class ImageStore(Protocol):
    def save(self, file: ImageFile) -> str: ...
