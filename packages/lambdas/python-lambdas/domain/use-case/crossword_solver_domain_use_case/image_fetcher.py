from typing import Protocol

from crossword_solver_domain_entities.image_file import ImageFile


class ImageFetcher(Protocol):
    def fetch(self, image_url: str, max_bytes: int) -> ImageFile: ...
