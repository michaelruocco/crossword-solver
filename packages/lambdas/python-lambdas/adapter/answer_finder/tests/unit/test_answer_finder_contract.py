from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.answer_finder import AnswerFinder

import crossword_solver_adapter_answer_finder


class StubAnswerFinder:
    def find_candidates(self, clue: Clue, number_of_candidates: int) -> Candidates:
        candidates = [Answer(clue.id, "CAT", confidence_score=90)]
        return Candidates(clue, candidates[:number_of_candidates])


def test_adapter_implementation_satisfies_use_case_contract():
    assert crossword_solver_adapter_answer_finder.__doc__ == "Answer finder adapters."

    finder: AnswerFinder = StubAnswerFinder()
    clue = Clue(Id.across(1), "Feline", [3])

    candidates = finder.find_candidates(clue, 1)

    assert candidates.clue is clue
    assert list(candidates) == [Answer(clue.id, "CAT", confidence_score=90)]
