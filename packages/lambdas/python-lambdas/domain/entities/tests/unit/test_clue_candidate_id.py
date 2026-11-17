from dataclasses import FrozenInstanceError

import pytest

from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId


def test_clue_candidate_id_is_a_value_object():
    first = ClueCandidateId(text="Feline", pattern="C??")
    second = ClueCandidateId(text="Feline", pattern="C??")

    assert first == second
    assert hash(first) == hash(second)
    assert first.text == "Feline"
    assert first.pattern == "C??"


def test_clue_candidate_id_is_immutable():
    candidate_id = ClueCandidateId(text="Feline", pattern="C??")
    attribute = "text"

    with pytest.raises(FrozenInstanceError):
        setattr(candidate_id, attribute, "Canine")
