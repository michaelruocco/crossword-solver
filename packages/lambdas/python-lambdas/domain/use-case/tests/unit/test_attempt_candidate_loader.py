from unittest.mock import Mock
from uuid import uuid4

import pytest
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.attempt_candidate_loader import AttemptCandidateLoader
from crossword_solver_domain_use_case.attempt_finder import AttemptFinder
from crossword_solver_domain_use_case.candidate_loader import CandidateLoader


def test_loads_candidates_for_a_clue_in_the_requested_attempt():
    puzzle_id = uuid4()
    attempt_id = uuid4()
    clue = Clue(Id.across(23), "Feline", [3], pattern="C??")
    attempt = Mock()
    attempt.puzzle.clues.find.return_value = clue
    attempt_finder = Mock(spec=AttemptFinder)
    attempt_finder.find_by_id.return_value = attempt
    candidates = Candidates(clue)
    candidate_loader = Mock(spec=CandidateLoader)
    candidate_loader.load_candidates.return_value = candidates

    result = AttemptCandidateLoader(attempt_finder, candidate_loader).load_candidates(puzzle_id, attempt_id, clue.id)

    assert result is candidates
    attempt_finder.find_by_id.assert_called_once_with(puzzle_id, attempt_id)
    attempt.puzzle.clues.find.assert_called_once_with(clue.id)
    candidate_loader.load_candidates.assert_called_once_with(clue)


def test_raises_when_clue_does_not_belong_to_attempt():
    clue_id = Id.across(23)
    attempt = Mock()
    attempt.puzzle.clues.find.return_value = None
    attempt_finder = Mock(spec=AttemptFinder)
    attempt_finder.find_by_id.return_value = attempt
    candidate_loader = Mock(spec=CandidateLoader)

    with pytest.raises(ClueNotFoundForIdError):
        AttemptCandidateLoader(attempt_finder, candidate_loader).load_candidates(uuid4(), uuid4(), clue_id)

    candidate_loader.load_candidates.assert_not_called()
