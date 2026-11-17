from typing import Protocol

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId


class CandidateRepository(Protocol):
    def save(self, candidates: Candidates) -> None: ...

    def get(self, clue: Clue) -> Candidates | None: ...

    def delete_all(self) -> None: ...

    def delete(self, candidate_id: ClueCandidateId) -> None: ...
