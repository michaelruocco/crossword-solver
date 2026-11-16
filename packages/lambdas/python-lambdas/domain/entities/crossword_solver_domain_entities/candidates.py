from collections.abc import Collection, Iterator

from .answer import Answer
from .candidates_score import CandidatesScore
from .clue import Clue
from .id import Id


class Candidates:
    def __init__(self, clue: Clue, values: Collection[Answer] | None = None):
        self._clue = clue
        self._values = list(values or [])

    @property
    def id(self) -> Id:
        return self._clue.id

    @property
    def clue(self) -> Clue:
        return self._clue

    def __iter__(self) -> Iterator[Answer]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def with_clue(self, clue: Clue) -> Candidates:
        return Candidates(clue, [answer.with_id(clue.id) for answer in self])

    def add_all(self, other_candidates: Candidates) -> Candidates:
        values_by_answer = {answer.value: answer for answer in self}
        values_by_answer.update({answer.value: answer for answer in other_candidates})
        return Candidates(self.clue, list(values_by_answer.values()))

    def size(self) -> int:
        return len(self._values)

    def best_score(self) -> int:
        best = self.best()
        return best.confidence_score if best else 0

    def alternative_scores(self) -> list[int]:
        return [answer.confidence_score for answer in self._values[1:]]

    def best(self) -> Answer | None:
        if not self._values:
            return None
        return max(self._values, key=lambda answer: answer.confidence_score)

    def get_best_answer_if_overall_score_greater_than(self, min_overall_score: float) -> Answer | None:
        if self.is_empty() or self.overall_score() <= min_overall_score:
            return None
        return self.best()

    def valid_answers(self, clue: Clue) -> Candidates:
        return Candidates(clue, [answer for answer in self if _matches_clue(answer, clue)])

    def is_empty(self) -> bool:
        return not self._values

    def as_string(self) -> str:
        return (
            f"clue {self.clue.id} {self.clue.text} {self.clue.pattern} -> "
            f"has {self.size()} candidates and best score {self.best_score()} {self.values_as_string()}"
        )

    def values_as_string(self) -> str:
        return ", ".join(answer.value for answer in self)

    def overall_score(self) -> float:
        return self.score().overall_score()

    def score(self) -> CandidatesScore:
        return CandidatesScore(
            best_score=self.best_score(),
            alternative_scores=self.alternative_scores(),
            number_of_candidates=self.size(),
            known_letter_count=self.clue.known_letter_count,
            total_letter_count=self.clue.total_length,
        )


def _matches_clue(answer: Answer, clue: Clue) -> bool:
    normalized_value = answer.normalized_value
    return len(normalized_value) == clue.total_length and answer.matches(clue.pattern)
