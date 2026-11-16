from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .clue_type import ClueType
from .hyphen_normalizer import normalize_hyphens
from .id import Id

if TYPE_CHECKING:
    from .candidates import Candidates


@dataclass(frozen=True)
class Clue:
    id: Id
    text: str
    lengths: list[int]
    type: ClueType | None = None
    pattern: str = ""
    candidates: Candidates | None = None

    UNKNOWN = "?"

    def __post_init__(self) -> None:
        pattern = self.pattern or self.UNKNOWN * self.total_length
        object.__setattr__(self, "pattern", pattern)

    @property
    def numeric_id(self) -> int:
        return self.id.number

    @property
    def direction(self):
        return self.id.direction

    @property
    def total_length(self) -> int:
        return sum(self.lengths)

    @property
    def known_letter_count(self) -> int:
        return len(self.pattern.replace(self.UNKNOWN, ""))

    def as_string(self) -> str:
        if self.known_letter_count:
            return f"{self.id} {self.text} {self.pattern}"
        return f"{self.id} {self.text}"

    def with_id(self, clue_id: Id) -> Clue:
        return Clue(clue_id, self.text, self.lengths, self.type, self.pattern, self.candidates)

    def with_text(self, text: str) -> Clue:
        return Clue(self.id, text, self.lengths, self.type, self.pattern, self.candidates)

    def normalize_hyphens(self) -> Clue:
        return Clue(
            id=self.id,
            text=normalize_hyphens(self.text),
            lengths=self.lengths,
            type=self.type,
            pattern=self.pattern,
            candidates=self.candidates,
        )

    def with_type(self, clue_type: ClueType) -> Clue:
        return Clue(
            id=self.id,
            text=self.text,
            lengths=self.lengths,
            type=clue_type,
            pattern=self.pattern,
            candidates=self.candidates,
        )

    def with_pattern(self, pattern: str) -> Clue:
        return Clue(
            id=self.id,
            text=self.text,
            lengths=self.lengths,
            type=self.type,
            pattern=pattern,
            candidates=self.candidates,
        )

    def with_candidates(self, candidates: Candidates) -> Clue:
        return Clue(
            id=self.id,
            text=self.text,
            lengths=self.lengths,
            type=self.type,
            pattern=self.pattern,
            candidates=candidates,
        )
