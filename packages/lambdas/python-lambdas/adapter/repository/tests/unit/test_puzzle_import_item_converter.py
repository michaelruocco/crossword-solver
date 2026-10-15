from datetime import UTC, datetime, timedelta
from uuid import uuid4

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from crossword_solver_adapter_repository.puzzle_import_item_converter import PuzzleImportItemConverter

CREATED_AT = datetime(2026, 10, 15, 9, 30, 0, tzinfo=UTC)


def a_puzzle_import() -> PuzzleImport:
    return PuzzleImport(
        id=uuid4(),
        image_url="https://example.com/puzzle24.jpg",
        status=PuzzleImportStatus.PENDING,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def test_to_item_sets_expiry_epoch_after_created_at_plus_ttl():
    converter = PuzzleImportItemConverter(ttl=timedelta(days=2))

    item = converter.to_item(a_puzzle_import())

    assert item["expires_at"] == int((CREATED_AT + timedelta(days=2)).timestamp())


def test_to_item_expires_after_seven_days_by_default():
    item = PuzzleImportItemConverter().to_item(a_puzzle_import())

    assert item["expires_at"] == int((CREATED_AT + timedelta(days=7)).timestamp())


def test_to_puzzle_import_ignores_expiry():
    converter = PuzzleImportItemConverter()
    puzzle_import = a_puzzle_import()

    assert converter.to_puzzle_import(converter.to_item(puzzle_import)) == puzzle_import
