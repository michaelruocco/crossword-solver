from uuid import UUID

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.id import Id

from .attempt_answer_deleter import AttemptAnswerDeleter
from .attempt_answer_saver import AttemptAnswerSaver
from .attempt_finder import AttemptFinder
from .attempt_repository import AttemptRepository


class AttemptAnswerService:
    def __init__(self, finder: AttemptFinder, repository: AttemptRepository):
        self.finder = finder
        self.saver = AttemptAnswerSaver(finder, repository)
        self.deleter = AttemptAnswerDeleter(finder, repository)

    def update_answer(self, puzzle_id: UUID, attempt_id: UUID, answer: Answer) -> Attempt:
        self.saver.save(puzzle_id, attempt_id, answer)
        return self.finder.find_by_id(puzzle_id, attempt_id)

    def delete_answer(self, puzzle_id: UUID, attempt_id: UUID, answer_id: Id) -> Attempt:
        self.deleter.delete(puzzle_id, attempt_id, answer_id)
        return self.finder.find_by_id(puzzle_id, attempt_id)
