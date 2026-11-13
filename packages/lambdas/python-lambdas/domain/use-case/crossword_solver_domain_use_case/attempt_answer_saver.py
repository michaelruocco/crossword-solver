from uuid import UUID

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.invalid_answer_error import InvalidAnswerError

from .attempt_finder import AttemptFinder
from .attempt_repository import AttemptRepository


class AttemptAnswerSaver:
    def __init__(self, finder: AttemptFinder, repository: AttemptRepository):
        self.finder = finder
        self.repository = repository

    def save(self, puzzle_id: UUID, attempt_id: UUID, answer: Answer) -> None:
        attempt = self.finder.find_by_id(puzzle_id, attempt_id)
        updated_attempt = attempt.save_answer(answer)
        if not attempt.accepts(answer):
            raise InvalidAnswerError(answer.id)
        self.repository.save(updated_attempt)
