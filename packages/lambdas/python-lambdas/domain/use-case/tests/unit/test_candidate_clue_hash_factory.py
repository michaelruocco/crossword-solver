import hashlib

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.candidate_clue_hash_factory import CandidateClueHashFactory


def test_hashes_clue_text_and_pattern_using_java_compatible_input():
    clue = Clue(Id.across(1), "Feline", [3], pattern="C??")
    expected = hashlib.sha256(b"Feline-C??").hexdigest()

    assert CandidateClueHashFactory().to_hash(clue) == expected


def test_hashes_candidate_id_identically_to_matching_clue():
    clue = Clue(Id.across(1), "Feline", [3], pattern="C??")
    candidate_id = ClueCandidateId(text=clue.text, pattern=clue.pattern)
    factory = CandidateClueHashFactory()

    assert factory.to_hash(candidate_id) == factory.to_hash(clue)
