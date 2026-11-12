from collections.abc import Collection, Iterator

from .answer import Answer
from .id import Id


class Answers:
    def __init__(self, values: Collection[Answer] | None = None):
        self._values = {answer.id: answer for answer in values or []}

    def __iter__(self) -> Iterator[Answer]:
        return iter(self._values.values())

    def __len__(self) -> int:
        return len(self._values)

    def find(self, answer_id: Id) -> Answer | None:
        return self._values.get(answer_id)

    def save(self, answer: Answer) -> Answers:
        updated_values = self._values.copy()
        updated_values[answer.id] = answer
        return Answers(updated_values.values())
