from unittest.mock import Mock

import boto3
import pytest
from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.id import Id
from moto import mock_aws

from crossword_solver_adapter_repository.dynamo_candidate_repository import DynamoCandidateRepository

CANDIDATES_TABLE = "candidates"


@pytest.fixture
def repository():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
        dynamodb.create_table(
            TableName=CANDIDATES_TABLE,
            KeySchema=[{"AttributeName": "candidate_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "candidate_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoCandidateRepository(CANDIDATES_TABLE, dynamodb=dynamodb)


def a_clue(clue_id=None, pattern="C??"):
    return Clue(
        id=clue_id or Id.across(1),
        text="Feline",
        lengths=[3],
        type=ClueType.STANDARD,
        pattern=pattern,
    )


def test_saves_and_gets_candidates_for_matching_clue(repository):
    clue = a_clue()
    candidates = Candidates(
        clue,
        [
            Answer(clue.id, "CAT", confidence_score=90),
            Answer(clue.id, "COT", confidence_score=75),
        ],
    )

    repository.save(candidates)
    restored = repository.get(clue)

    assert restored is not None
    assert restored.clue is clue
    assert list(restored) == list(candidates)
    item = repository.table.get_item(Key={"candidate_id": repository.hash_factory.to_hash(clue)})["Item"]
    assert item["text"] == clue.text
    assert item["pattern"] == clue.pattern
    assert item["type"] == "STANDARD"


def test_get_reassigns_answer_ids_to_the_requested_clue(repository):
    original_clue = a_clue()
    repository.save(Candidates(original_clue, [Answer(original_clue.id, "CAT", 90)]))
    requested_clue = a_clue(clue_id=Id.down(7))

    restored = repository.get(requested_clue)

    assert restored is not None
    assert restored.clue is requested_clue
    assert list(restored) == [Answer(requested_clue.id, "CAT", 90)]


def test_get_returns_none_when_candidates_do_not_exist(repository):
    assert repository.get(a_clue()) is None


def test_delete_removes_candidates_for_text_and_pattern(repository):
    clue = a_clue()
    repository.save(Candidates(clue, [Answer(clue.id, "CAT", 90)]))

    repository.delete(ClueCandidateId(text=clue.text, pattern=clue.pattern))

    assert repository.get(clue) is None


def test_delete_all_removes_every_candidate(repository):
    first = a_clue()
    second = a_clue(clue_id=Id.down(2), pattern="D??")
    repository.save(Candidates(first, [Answer(first.id, "CAT", 90)]))
    repository.save(Candidates(second, [Answer(second.id, "DOG", 90)]))

    repository.delete_all()

    assert repository.get(first) is None
    assert repository.get(second) is None


def test_delete_all_deletes_candidates_from_all_scan_pages(repository, monkeypatch):
    first = a_clue()
    second = a_clue(clue_id=Id.down(2), pattern="D??")
    repository.save(Candidates(first, [Answer(first.id, "CAT", 90)]))
    repository.save(Candidates(second, [Answer(second.id, "DOG", 90)]))
    first_key = repository.hash_factory.to_hash(first)
    second_key = repository.hash_factory.to_hash(second)
    first_page_key = {"candidate_id": first_key}
    scan = Mock(
        side_effect=[
            {"Items": [{"candidate_id": first_key}], "LastEvaluatedKey": first_page_key},
            {"Items": [{"candidate_id": second_key}]},
        ]
    )
    monkeypatch.setattr(repository.table, "scan", scan)

    repository.delete_all()

    assert scan.call_count == 2
    assert scan.call_args_list[0].kwargs == {"ProjectionExpression": "candidate_id"}
    assert scan.call_args_list[1].kwargs == {
        "ProjectionExpression": "candidate_id",
        "ExclusiveStartKey": first_page_key,
    }
    assert repository.get(first) is None
    assert repository.get(second) is None


def test_delete_all_does_not_open_batch_writer_when_table_is_empty(repository):
    batch_writer = Mock()
    repository.table.batch_writer = batch_writer

    repository.delete_all()

    batch_writer.assert_not_called()
