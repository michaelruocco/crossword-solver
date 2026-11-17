from concurrent.futures import Future, ThreadPoolExecutor
from unittest.mock import Mock

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.candidate_batch_loader import CandidateBatchLoader


def a_clue(number: int) -> Clue:
    return Clue(Id.across(number), f"Clue {number}", [3])


def test_loads_candidates_for_each_clue_concurrently():
    clues = Clues([a_clue(1), a_clue(2)])
    first, second = list(clues)
    candidate_loader = Mock()

    def load_for_clue(clue, _candidates_per_clue):
        answer = "CAT" if clue.id == first.id else "DOG"
        score = 90 if clue.id == first.id else 80
        return Candidates(clue, [Answer(clue.id, answer, score)])

    candidate_loader.load_candidates.side_effect = load_for_clue

    with ThreadPoolExecutor(max_workers=2) as executor:
        result = CandidateBatchLoader(candidate_loader, executor).load_candidates(clues, candidates_per_clue=4)

    assert set(result) == {first.id, second.id}
    assert list(result[first.id]) == [Answer(first.id, "CAT", 90)]
    assert list(result[second.id]) == [Answer(second.id, "DOG", 80)]
    assert all(call.args[1] == 4 for call in candidate_loader.load_candidates.call_args_list)


def test_returns_empty_candidates_for_a_clue_that_fails_to_load(caplog):
    clues = Clues([a_clue(1), a_clue(2)])
    first, second = list(clues)
    successful_candidates = Candidates(first, [Answer(first.id, "CAT", 90)])
    candidate_loader = Mock()

    def fail_for_second_clue(clue, _candidates_per_clue):
        if clue.id == second.id:
            raise RuntimeError("answer finder failed")
        return successful_candidates

    candidate_loader.load_candidates.side_effect = fail_for_second_clue

    with ThreadPoolExecutor(max_workers=2) as executor:
        result = CandidateBatchLoader(candidate_loader, executor).load_candidates(clues)

    assert result[first.id] is successful_candidates
    assert result[second.id].clue is second
    assert result[second.id].is_empty()
    assert f"candidate lookup failed for clue {second.id}" in caplog.text


def test_returns_empty_candidates_when_a_clue_load_times_out():
    clue = a_clue(1)
    future = Future()
    future.set_exception(TimeoutError())
    executor = Mock()
    executor.submit.return_value = future
    candidate_loader = Mock()

    result = CandidateBatchLoader(candidate_loader, executor, timeout_seconds=0.01).load_candidates(Clues([clue]))

    assert list(result) == [clue.id]
    assert result[clue.id].clue is clue
    assert result[clue.id].is_empty()
    executor.submit.assert_called_once_with(candidate_loader.load_candidates, clue, 5)
