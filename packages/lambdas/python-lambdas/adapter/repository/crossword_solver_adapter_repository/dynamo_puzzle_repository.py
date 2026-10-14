from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_use_case.puzzle_repository import PuzzleRepository

from .puzzle_item_converter import PuzzleItemConverter


class DynamoPuzzleRepository(PuzzleRepository):
    HASH_INDEX_NAME = "hash-index"

    def __init__(
        self,
        table_name: str,
        dynamodb=None,
        converter: PuzzleItemConverter | None = None,
    ):
        self.table = (dynamodb or boto3.resource("dynamodb")).Table(table_name)
        self.converter = converter or PuzzleItemConverter()

    def find_all(self) -> list[Puzzle]:
        response = self.table.scan()
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response["Items"])
        return [self.converter.to_puzzle(item) for item in items]

    def find_by_id(self, puzzle_id: UUID) -> Puzzle | None:
        item = self.table.get_item(Key={"id": str(puzzle_id)}, ConsistentRead=True).get("Item")
        return self.converter.to_puzzle(item) if item else None

    def find_by_hash(self, hash: str) -> Puzzle | None:
        items = self.table.query(
            IndexName=self.HASH_INDEX_NAME,
            KeyConditionExpression=Key("hash").eq(hash),
            Limit=1,
        )["Items"]
        return self.converter.to_puzzle(items[0]) if items else None

    def save(self, puzzle: Puzzle) -> None:
        self.table.put_item(Item=self.converter.to_item(puzzle))

    def delete_by_id(self, puzzle_id: UUID) -> None:
        self.table.delete_item(Key={"id": str(puzzle_id)})
