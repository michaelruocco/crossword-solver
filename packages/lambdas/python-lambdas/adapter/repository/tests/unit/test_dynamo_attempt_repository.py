from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import boto3
import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.words import Words
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from moto import mock_aws

from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository

ATTEMPTS_TABLE = "attempts"
PUZZLES_TABLE = "puzzles"
CREATED_AT = datetime(2026, 10, 31, 9, 30, tzinfo=UTC)


@pytest.fixture
def repositories():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
        dynamodb.create_table(
            TableName=PUZZLES_TABLE,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb.create_table(
            TableName=ATTEMPTS_TABLE,
            KeySchema=[
                {"AttributeName": "puzzle_id", "KeyType": "HASH"},
                {"AttributeName": "attempt_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "puzzle_id", "AttributeType": "S"},
                {"AttributeName": "attempt_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        puzzle_repository = DynamoPuzzleRepository(PUZZLES_TABLE, dynamodb=dynamodb)
        attempt_repository = DynamoAttemptRepository(
            ATTEMPTS_TABLE,
            PUZZLES_TABLE,
            puzzle_repository,
            dynamodb=dynamodb,
        )
        yield attempt_repository, puzzle_repository


def a_puzzle(puzzle_id=None) -> Puzzle:
    return Puzzle(
        id=puzzle_id or uuid4(),
        name="test-puzzle",
        format=".png",
        hash=str(uuid4()),
        clues=Clues([]),
        grid=Grid(Cells([Cell(Coordinates(0, 0), black=False)]), column_width=1, row_height=1),
        words=Words([]),
        created_at=CREATED_AT,
    )


def an_attempt(puzzle: Puzzle, attempt_id=None) -> Attempt:
    return Attempt(id=attempt_id or uuid4(), created_at=CREATED_AT, puzzle=puzzle)


def test_saves_attempt_by_reference_and_hydrates_puzzle_on_load(repositories):
    attempts, puzzles = repositories
    puzzle = a_puzzle()
    attempt = an_attempt(puzzle)
    puzzles.save(puzzle)

    attempts.save(attempt)
    item = attempts.table.get_item(
        Key={"puzzle_id": str(puzzle.id), "attempt_id": str(attempt.id)},
        ConsistentRead=True,
    )["Item"]
    restored = attempts.find_by_id(puzzle.id, attempt.id)

    assert set(item) == {"puzzle_id", "attempt_id", "created_at", "solving", "answer_count"}
    assert item["puzzle_id"] == str(puzzle.id)
    assert restored is not None
    assert restored.id == attempt.id
    assert restored.created_at == attempt.created_at
    assert restored.puzzle.id == puzzle.id
    assert restored.puzzle.name == puzzle.name
    assert restored.puzzle.grid == puzzle.grid


def test_find_by_id_returns_none_when_attempt_does_not_exist(repositories):
    attempts, _ = repositories

    assert attempts.find_by_id(uuid4(), uuid4()) is None


def test_find_by_id_returns_none_when_referenced_puzzle_does_not_exist(repositories):
    attempts, _ = repositories
    puzzle = a_puzzle()
    attempt = an_attempt(puzzle)
    attempts.table.put_item(Item=attempts.converter.to_item(attempt))

    assert attempts.find_by_id(puzzle.id, attempt.id) is None


def test_find_by_puzzle_reads_all_pages_and_sorts_attempts_newest_first(repositories):
    attempts, puzzles = repositories
    puzzle = a_puzzle()
    puzzles.save(puzzle)
    older = Attempt(uuid4(), datetime(2026, 10, 30, 9, 30, tzinfo=UTC), puzzle)
    newer = Attempt(uuid4(), datetime(2026, 10, 31, 9, 30, tzinfo=UTC), puzzle)
    attempts.save(older)
    attempts.save(newer)

    result = attempts.find_by_puzzle(puzzle)

    assert [attempt.id for attempt in result] == [newer.id, older.id]
    assert all(attempt.puzzle is puzzle for attempt in result)


def test_find_by_puzzle_uses_exclusive_start_key_for_query_pages():
    puzzle = a_puzzle()
    first_item = {
        "puzzle_id": str(puzzle.id),
        "attempt_id": str(uuid4()),
        "created_at": CREATED_AT.isoformat(),
        "solving": False,
        "answer_count": 0,
    }
    second_item = {**first_item, "attempt_id": str(uuid4())}
    dynamodb = MagicMock()
    table = dynamodb.Table.return_value
    table.query.side_effect = [
        {"Items": [first_item], "LastEvaluatedKey": first_item},
        {"Items": [second_item]},
    ]
    repository = DynamoAttemptRepository(ATTEMPTS_TABLE, PUZZLES_TABLE, Mock(), dynamodb=dynamodb)

    result = repository.find_by_puzzle(puzzle)

    assert len(result) == 2
    assert table.query.call_args_list[1].kwargs["ExclusiveStartKey"] == first_item


def test_save_condition_checks_puzzle_and_writes_attempt_in_one_transaction():
    puzzle = a_puzzle()
    attempt = an_attempt(puzzle)
    dynamodb = MagicMock()
    dynamodb.Table.return_value.name = ATTEMPTS_TABLE
    attempt_repository = DynamoAttemptRepository(
        ATTEMPTS_TABLE,
        PUZZLES_TABLE,
        Mock(),
        dynamodb=dynamodb,
    )

    attempt_repository.save(attempt)

    transaction = dynamodb.meta.client.transact_write_items.call_args.kwargs["TransactItems"]
    assert transaction[0] == {
        "ConditionCheck": {
            "TableName": PUZZLES_TABLE,
            "Key": {"id": str(puzzle.id)},
            "ConditionExpression": "attribute_exists(id)",
        }
    }
    assert transaction[1] == {
        "Put": {
            "TableName": ATTEMPTS_TABLE,
            "Item": {
                "puzzle_id": str(puzzle.id),
                "attempt_id": str(attempt.id),
                "created_at": CREATED_AT.isoformat(),
                "solving": False,
                "answer_count": 0,
            },
        }
    }


def test_save_rejects_an_attempt_for_a_puzzle_deleted_before_commit(repositories):
    attempts, _ = repositories
    puzzle = a_puzzle()
    attempt = an_attempt(puzzle)

    attempts.puzzle_repository.find_by_id = Mock(return_value=None)
    attempts.dynamodb.meta.client.transact_write_items = Mock(
        side_effect=ClientError(
            {"Error": {"Code": "TransactionCanceledException", "Message": "condition failed"}},
            "TransactWriteItems",
        )
    )

    with pytest.raises(PuzzleNotFoundError):
        attempts.save(attempt)


@pytest.mark.parametrize("error_code", ["ProvisionedThroughputExceededException", "TransactionCanceledException"])
def test_save_propagates_client_errors_when_puzzle_still_exists(error_code):
    puzzle = a_puzzle()
    attempt = an_attempt(puzzle)
    error = ClientError(
        {"Error": {"Code": error_code, "Message": "transaction failed"}},
        "TransactWriteItems",
    )
    dynamodb = MagicMock()
    dynamodb.meta.client.transact_write_items.side_effect = error
    puzzle_repository = Mock()
    puzzle_repository.find_by_id.return_value = puzzle
    attempts = DynamoAttemptRepository(
        ATTEMPTS_TABLE,
        PUZZLES_TABLE,
        puzzle_repository,
        dynamodb=dynamodb,
    )

    with pytest.raises(ClientError) as raised:
        attempts.save(attempt)

    assert raised.value is error
    if error_code == "TransactionCanceledException":
        puzzle_repository.find_by_id.assert_called_once_with(puzzle.id)
    else:
        puzzle_repository.find_by_id.assert_not_called()


def test_delete_by_puzzle_id_deletes_attempts_from_every_query_page():
    puzzle_id = uuid4()
    first_key = {"puzzle_id": str(puzzle_id), "attempt_id": str(uuid4())}
    second_key = {"puzzle_id": str(puzzle_id), "attempt_id": str(uuid4())}
    dynamodb = MagicMock()
    table = dynamodb.Table.return_value
    table.query.side_effect = [
        {"Items": [first_key], "LastEvaluatedKey": first_key},
        {"Items": [second_key]},
    ]
    attempts = DynamoAttemptRepository(ATTEMPTS_TABLE, PUZZLES_TABLE, Mock(), dynamodb=dynamodb)

    attempts.delete_by_puzzle_id(puzzle_id)

    assert table.query.call_count == 2
    assert table.query.call_args_list[0].kwargs == {
        "KeyConditionExpression": Key("puzzle_id").eq(str(puzzle_id)),
        "ProjectionExpression": "puzzle_id, attempt_id",
    }
    assert table.query.call_args_list[1].kwargs == {
        "KeyConditionExpression": Key("puzzle_id").eq(str(puzzle_id)),
        "ProjectionExpression": "puzzle_id, attempt_id",
        "ExclusiveStartKey": first_key,
    }
    batch = table.batch_writer.return_value.__enter__.return_value
    assert batch.delete_item.call_count == 2
    batch.delete_item.assert_any_call(Key=first_key)
    batch.delete_item.assert_any_call(Key=second_key)


def test_delete_by_puzzle_id_does_not_open_batch_writer_when_no_attempts_exist():
    dynamodb = MagicMock()
    table = dynamodb.Table.return_value
    table.query.return_value = {"Items": []}
    attempts = DynamoAttemptRepository(ATTEMPTS_TABLE, PUZZLES_TABLE, Mock(), dynamodb=dynamodb)

    attempts.delete_by_puzzle_id(uuid4())

    table.query.assert_called_once()
    table.batch_writer.assert_not_called()


def test_delete_by_puzzle_id_removes_only_that_puzzles_attempts(repositories):
    attempts, puzzles = repositories
    puzzle = a_puzzle()
    other_puzzle = a_puzzle()
    puzzles.save(puzzle)
    puzzles.save(other_puzzle)
    puzzle_attempts = [an_attempt(puzzle), an_attempt(puzzle)]
    other_attempt = an_attempt(other_puzzle)
    for attempt in [*puzzle_attempts, other_attempt]:
        attempts.table.put_item(Item=attempts.converter.to_item(attempt))

    attempts.delete_by_puzzle_id(puzzle.id)

    assert all(attempts.find_by_id(puzzle.id, attempt.id) is None for attempt in puzzle_attempts)
    restored_other_attempt = attempts.find_by_id(other_puzzle.id, other_attempt.id)
    assert restored_other_attempt is not None
    assert restored_other_attempt.id == other_attempt.id
    assert restored_other_attempt.puzzle.id == other_puzzle.id
