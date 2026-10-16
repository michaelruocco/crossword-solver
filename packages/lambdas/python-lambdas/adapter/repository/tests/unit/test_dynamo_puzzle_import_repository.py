from datetime import UTC, datetime
from uuid import uuid4

import boto3
import pytest
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus
from moto import mock_aws

from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository

TABLE_NAME = "puzzle-imports"


@pytest.fixture
def repository():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoPuzzleImportRepository(TABLE_NAME, dynamodb=dynamodb)


def a_pending_import() -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url="https://example.com/puzzle24.jpg",
        status=PuzzleImportStatus.PENDING,
        created_at=datetime(2026, 10, 15, 9, 30, 15, 123456, tzinfo=UTC),
        updated_at=datetime(2026, 10, 15, 9, 30, 15, 123456, tzinfo=UTC),
    )


def test_find_by_id_returns_saved_pending_import(repository):
    puzzle_import = a_pending_import()
    repository.save(puzzle_import)

    assert repository.find_by_id(puzzle_import.id) == puzzle_import


def test_find_by_id_returns_saved_import_with_its_source_url(repository):
    puzzle_import = a_pending_import()
    puzzle_import.source_url = "https://example.com/original/puzzle24.jpg"
    repository.save(puzzle_import)

    assert repository.find_by_id(puzzle_import.id) == puzzle_import


def test_find_by_id_returns_saved_complete_import(repository):
    puzzle_import = a_pending_import()
    puzzle_import.status = PuzzleImportStatus.COMPLETE
    puzzle_import.puzzle_id = uuid4()
    repository.save(puzzle_import)

    assert repository.find_by_id(puzzle_import.id) == puzzle_import


def test_find_by_id_returns_saved_failed_import(repository):
    puzzle_import = a_pending_import()
    puzzle_import.status = PuzzleImportStatus.FAILED
    puzzle_import.error = "Failed to download image"
    repository.save(puzzle_import)

    assert repository.find_by_id(puzzle_import.id) == puzzle_import


def test_find_by_id_returns_none_when_not_found(repository):
    assert repository.find_by_id(uuid4()) is None


def test_save_overwrites_import_with_same_id(repository):
    puzzle_import = a_pending_import()
    repository.save(puzzle_import)
    puzzle_import.status = PuzzleImportStatus.COMPLETE
    puzzle_import.puzzle_id = uuid4()
    repository.save(puzzle_import)

    found = repository.find_by_id(puzzle_import.id)

    assert found is not None
    assert found.status == PuzzleImportStatus.COMPLETE
    assert found.puzzle_id == puzzle_import.puzzle_id
