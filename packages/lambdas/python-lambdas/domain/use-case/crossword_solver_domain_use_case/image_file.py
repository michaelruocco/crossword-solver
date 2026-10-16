from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class ImageFile:
    filename: str
    content: bytes

    @property
    def name(self) -> str:
        return PurePosixPath(self.filename).stem

    @property
    def format(self) -> str:
        return PurePosixPath(self.filename).suffix
