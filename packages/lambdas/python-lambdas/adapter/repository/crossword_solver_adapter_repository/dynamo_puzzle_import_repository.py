from uuid import UUID

import boto3
from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_use_case.puzzle_import_repository import PuzzleImportRepository

from .puzzle_import_item_converter import PuzzleImportItemConverter


class DynamoPuzzleImportRepository(PuzzleImportRepository):
    def __init__(
        self,
        table_name: str,
        dynamodb=None,
        converter: PuzzleImportItemConverter | None = None,
    ):
        self.table = (dynamodb or boto3.resource("dynamodb")).Table(table_name)
        self.converter = converter or PuzzleImportItemConverter()

    def find_by_id(self, import_id: UUID) -> PuzzleImport | None:
        item = self.table.get_item(Key={"id": str(import_id)}, ConsistentRead=True).get("Item")
        return self.converter.to_puzzle_import(item) if item else None

    def save(self, puzzle_import: PuzzleImport) -> None:
        self.table.put_item(Item=self.converter.to_item(puzzle_import))
