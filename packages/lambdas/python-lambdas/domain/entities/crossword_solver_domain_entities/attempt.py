from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .answer import Answer
from .answers import Answers
from .clue_not_found_for_id_error import ClueNotFoundForIdError
from .puzzle import Puzzle


@dataclass
class Attempt:
    id: UUID
    created_at: datetime
    puzzle: Puzzle
    solving: bool = False
    answer_count: int = 0
    answers: Answers = field(default_factory=Answers)

    @property
    def puzzle_id(self) -> UUID:
        return self.puzzle.id

    def accepts(self, answer: Answer) -> bool:
        clue = self.puzzle.clues.find(answer.id)
        if clue is None or len(answer.normalized_value) != clue.total_length:
            return False

        for intersection in self.puzzle.intersections(answer.id):
            intersecting_answer = self.answers.find(intersection.to_intersecting_id(answer.id))
            if intersecting_answer and answer.conflicts_with(intersecting_answer, intersection):
                return False
        return True

    def save_answer(self, answer: Answer) -> Attempt:
        if not self.puzzle.clues.has_clue(answer.id):
            raise ClueNotFoundForIdError(answer.id)

        updated_answers = self.answers.save(answer)
        answer_count = self.answer_count + (self.answers.find(answer.id) is None)
        return Attempt(
            id=self.id,
            created_at=self.created_at,
            puzzle=self.puzzle,
            solving=self.solving,
            answer_count=answer_count,
            answers=updated_answers,
        )
