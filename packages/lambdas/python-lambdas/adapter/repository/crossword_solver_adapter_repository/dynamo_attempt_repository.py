from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_use_case.attempt_repository import AttemptRepository
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError
from crossword_solver_domain_use_case.puzzle_repository import PuzzleRepository

from .attempt_item_converter import AttemptItemConverter


class DynamoAttemptRepository(AttemptRepository):
    def __init__(
        self,
        table_name: str,
        puzzle_table_name: str,
        puzzle_repository: PuzzleRepository,
        dynamodb=None,
        converter: AttemptItemConverter | None = None,
    ):
        self.dynamodb = dynamodb or boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.puzzle_table_name = puzzle_table_name
        self.puzzle_repository = puzzle_repository
        self.converter = converter or AttemptItemConverter()

    def find_by_id(self, puzzle_id: UUID, attempt_id: UUID) -> Attempt | None:
        item = self.table.get_item(
            Key={"puzzle_id": str(puzzle_id), "attempt_id": str(attempt_id)},
            ConsistentRead=True,
        ).get("Item")
        if not item:
            return None

        puzzle = self.puzzle_repository.find_by_id(UUID(item["puzzle_id"]))
        if puzzle is None:
            return None
        return self.converter.to_attempt(item, puzzle)

    def save(self, attempt: Attempt) -> None:
        serializer = TypeSerializer()
        item = {key: serializer.serialize(value) for key, value in self.converter.to_item(attempt).items()}
        try:
            self.dynamodb.meta.client.transact_write_items(
                TransactItems=[
                    {
                        "ConditionCheck": {
                            "TableName": self.puzzle_table_name,
                            "Key": {"id": {"S": str(attempt.puzzle_id)}},
                            "ConditionExpression": "attribute_exists(id)",
                        }
                    },
                    {"Put": {"TableName": self.table.name, "Item": item}},
                ]
            )
        except ClientError as error:
            if error.response["Error"]["Code"] != "TransactionCanceledException":
                raise
            if self.puzzle_repository.find_by_id(attempt.puzzle_id) is None:
                raise PuzzleNotFoundError(attempt.puzzle_id) from error
            raise

    def delete_by_puzzle_id(self, puzzle_id: UUID) -> None:
        query = self.table.query(
            KeyConditionExpression=Key("puzzle_id").eq(str(puzzle_id)),
            ProjectionExpression="puzzle_id, attempt_id",
        )
        items = query["Items"]
        while "LastEvaluatedKey" in query:
            query = self.table.query(
                KeyConditionExpression=Key("puzzle_id").eq(str(puzzle_id)),
                ProjectionExpression="puzzle_id, attempt_id",
                ExclusiveStartKey=query["LastEvaluatedKey"],
            )
            items.extend(query["Items"])

        if items:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={"puzzle_id": item["puzzle_id"], "attempt_id": item["attempt_id"]})
