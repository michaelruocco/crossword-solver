from uuid import UUID

from crossword_solver_domain_entities.id import Id

from .attempt_finder import AttemptFinder
from .attempt_repository import AttemptRepository


class AttemptAnswerDeleter:
    def __init__(self, finder: AttemptFinder, repository: AttemptRepository):
        self.finder = finder
        self.repository = repository

    def delete(self, puzzle_id: UUID, attempt_id: UUID, answer_id: Id) -> None:
        attempt = self.finder.find_by_id(puzzle_id, attempt_id)
        self.repository.save(attempt.delete_answer(answer_id))
