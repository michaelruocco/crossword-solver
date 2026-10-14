from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import boto3
import pytest
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from moto import mock_aws

from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository

TABLE_NAME = "puzzles"


@pytest.fixture
def repository():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "hash", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": DynamoPuzzleRepository.HASH_INDEX_NAME,
                    "KeySchema": [{"AttributeName": "hash", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoPuzzleRepository(TABLE_NAME, dynamodb=dynamodb)


def a_puzzle(puzzle_id: UUID | None = None, hash: str = "hash-value") -> Puzzle:
    return Puzzle(
        id=puzzle_id or uuid4(),
        name="puzzle24",
        format=".jpg",
        hash=hash,
        clues=Clues(
            [
                Clue(Id.across(1), "Pacific republic (4)", [4], ClueType.CRYPTIC),
                Clue(Id.down(2), "Stale (3,3)", [3, 3]),
            ]
        ),
        grid=Grid(
            cells=Cells(
                [
                    Cell(Coordinates(0, 1), black=False, id=1, letter="F"),
                    Cell(Coordinates(1, 1), black=True),
                    Cell(Coordinates(0, 0), black=False),
                ]
            ),
            column_width=40,
            row_height=50,
        ),
        created_at=datetime(2026, 10, 14, 9, 30, 15, 123456, tzinfo=UTC),
    )


def assert_same_puzzle(actual: Puzzle | None, expected: Puzzle) -> None:
    assert actual is not None
    assert actual.id == expected.id
    assert actual.name == expected.name
    assert actual.format == expected.format
    assert actual.hash == expected.hash
    assert list(actual.clues) == list(expected.clues)
    assert actual.grid == expected.grid
    assert actual.created_at == expected.created_at


def test_find_by_id_returns_saved_puzzle(repository):
    puzzle = a_puzzle()
    repository.save(puzzle)

    assert_same_puzzle(repository.find_by_id(puzzle.id), puzzle)


def test_find_by_id_returns_none_when_not_found(repository):
    assert repository.find_by_id(uuid4()) is None


def test_find_by_hash_returns_saved_puzzle(repository):
    puzzle = a_puzzle(hash="abc123")
    repository.save(a_puzzle(hash="other"))
    repository.save(puzzle)

    assert_same_puzzle(repository.find_by_hash("abc123"), puzzle)


def test_find_by_hash_returns_none_when_not_found(repository):
    assert repository.find_by_hash("missing") is None


def test_find_all_returns_all_saved_puzzles(repository):
    puzzles = [a_puzzle(), a_puzzle()]
    for puzzle in puzzles:
        repository.save(puzzle)

    assert {puzzle.id for puzzle in repository.find_all()} == {puzzle.id for puzzle in puzzles}


def test_find_all_returns_empty_list_when_no_puzzles(repository):
    assert repository.find_all() == []


def test_find_all_reads_every_page():
    first, second = a_puzzle(), a_puzzle()
    dynamodb = MagicMock()
    repository = DynamoPuzzleRepository(TABLE_NAME, dynamodb=dynamodb)
    dynamodb.Table.return_value.scan.side_effect = [
        {"Items": [repository.converter.to_item(first)], "LastEvaluatedKey": {"id": str(first.id)}},
        {"Items": [repository.converter.to_item(second)]},
    ]

    assert [puzzle.id for puzzle in repository.find_all()] == [first.id, second.id]
    dynamodb.Table.return_value.scan.assert_called_with(ExclusiveStartKey={"id": str(first.id)})


def test_save_overwrites_puzzle_with_same_id(repository):
    puzzle_id = uuid4()
    repository.save(a_puzzle(puzzle_id, hash="first"))
    repository.save(a_puzzle(puzzle_id, hash="second"))

    found = repository.find_by_id(puzzle_id)

    assert found is not None
    assert found.hash == "second"


def test_delete_by_id_removes_puzzle(repository):
    puzzle = a_puzzle()
    repository.save(puzzle)

    repository.delete_by_id(puzzle.id)

    assert repository.find_by_id(puzzle.id) is None
