from unittest.mock import Mock

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.candidate_loader import CandidateLoader


def a_clue() -> Clue:
    return Clue(Id.across(1), "Feline", [3], pattern="C??")


def test_returns_cached_candidates_without_calling_answer_finder():
    clue = a_clue()
    cached_candidates = Candidates(clue, [Answer(clue.id, "CAT", 90)])
    answer_finder = Mock()
    repository = Mock()
    repository.get.return_value = cached_candidates

    result = CandidateLoader(answer_finder, repository).load_candidates(clue)

    assert result is cached_candidates
    repository.get.assert_called_once_with(clue)
    answer_finder.find_candidates.assert_not_called()
    repository.save.assert_not_called()


def test_finds_filters_and_saves_candidates_on_cache_miss():
    clue = a_clue()
    found_candidates = Candidates(
        clue,
        [
            Answer(clue.id, "CAT", 90),
            Answer(clue.id, "DOG", 80),
        ],
    )
    answer_finder = Mock()
    answer_finder.find_candidates.return_value = found_candidates
    repository = Mock()
    repository.get.return_value = None

    result = CandidateLoader(answer_finder, repository).load_candidates(clue, candidates_per_clue=3)

    assert list(result) == [Answer(clue.id, "CAT", 90)]
    answer_finder.find_candidates.assert_called_once_with(clue, 3)
    repository.save.assert_called_once_with(result)


def test_does_not_save_when_answer_finder_returns_no_valid_candidates():
    clue = a_clue()
    answer_finder = Mock()
    answer_finder.find_candidates.return_value = Candidates(clue, [Answer(clue.id, "DOG", 80)])
    repository = Mock()
    repository.get.return_value = None

    result = CandidateLoader(answer_finder, repository).load_candidates(clue)

    assert result.is_empty()
    repository.save.assert_not_called()
