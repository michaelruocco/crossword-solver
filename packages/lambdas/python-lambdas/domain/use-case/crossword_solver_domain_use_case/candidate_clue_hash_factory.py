import hashlib

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId


class CandidateClueHashFactory:
    def to_hash(self, clue_or_id: Clue | ClueCandidateId) -> str:
        value = f"{clue_or_id.text}-{clue_or_id.pattern}".encode()
        return hashlib.sha256(value).hexdigest()
