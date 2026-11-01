from typing import Protocol
from uuid import UUID

from crossword_solver_domain_entities.attempt import Attempt


class AttemptRepository(Protocol):
    def find_by_id(self, puzzle_id: UUID, attempt_id: UUID) -> Attempt | None: ...

    def save(self, attempt: Attempt) -> None: ...

    def delete_by_puzzle_id(self, puzzle_id: UUID) -> None: ...
