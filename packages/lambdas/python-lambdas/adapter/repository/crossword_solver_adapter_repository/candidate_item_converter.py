from typing import Any

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue

Item = dict[str, Any]


class CandidateItemConverter:
    def to_item(self, candidates: Candidates, candidate_id: str) -> Item:
        clue = candidates.clue
        return {
            "candidate_id": candidate_id,
            "text": clue.text,
            "type": clue.type.value if clue.type else None,
            "pattern": clue.pattern,
            "answers": [{"value": answer.value, "confidence_score": answer.confidence_score} for answer in candidates],
        }

    def to_candidates(self, item: Item, clue: Clue) -> Candidates:
        answers = [
            Answer(clue.id, answer["value"], int(answer.get("confidence_score", 0)))
            for answer in item.get("answers", [])
        ]
        return Candidates(clue, answers)
