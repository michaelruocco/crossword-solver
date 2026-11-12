from datetime import datetime
from typing import Any
from uuid import UUID

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.answers import Answers
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle

Item = dict[str, Any]


class AttemptItemConverter:
    def to_item(self, attempt: Attempt) -> Item:
        return {
            "puzzle_id": str(attempt.puzzle_id),
            "attempt_id": str(attempt.id),
            "created_at": attempt.created_at.isoformat(),
            "solving": attempt.solving,
            "answer_count": attempt.answer_count,
            "answers": {str(answer.id): answer.value for answer in attempt.answers},
        }

    def to_attempt(self, item: Item, puzzle: Puzzle) -> Attempt:
        answers = Answers(
            [
                Answer(
                    id=Id(int(answer_id[:-1]), Direction(answer_id[-1])),
                    value=value,
                )
                for answer_id, value in item.get("answers", {}).items()
            ]
        )
        return Attempt(
            id=UUID(item["attempt_id"]),
            created_at=datetime.fromisoformat(item["created_at"]),
            puzzle=puzzle,
            solving=item["solving"],
            answer_count=int(item["answer_count"]),
            answers=answers,
        )
