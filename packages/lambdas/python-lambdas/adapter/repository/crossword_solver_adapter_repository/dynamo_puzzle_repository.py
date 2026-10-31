import base64
import json
from uuid import UUID

from boto3.dynamodb.conditions import Key
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_use_case.invalid_puzzle_summary_cursor_error import InvalidPuzzleSummaryCursorError
from crossword_solver_domain_use_case.puzzle_repository import PuzzleRepository

from .dynamodb_resource import create_dynamodb_resource
from .puzzle_item_converter import PuzzleItemConverter


class DynamoPuzzleRepository(PuzzleRepository):
    HASH_INDEX_NAME = "hash-index"

    def __init__(
        self,
        table_name: str,
        dynamodb=None,
        converter: PuzzleItemConverter | None = None,
    ):
        self.table = (dynamodb or create_dynamodb_resource()).Table(table_name)
        self.converter = converter or PuzzleItemConverter()

    def find_all(self) -> list[Puzzle]:
        response = self.table.scan()
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response["Items"])
        return [self.converter.to_puzzle(item) for item in items]

    def find_page(self, limit: int, cursor: str | None = None) -> tuple[list[Puzzle], str | None]:
        scan_args = {"Limit": limit}
        if cursor is not None:
            scan_args["ExclusiveStartKey"] = _decode_cursor(cursor)

        response = self.table.scan(**scan_args)
        next_cursor = _encode_cursor(response["LastEvaluatedKey"]) if response.get("LastEvaluatedKey") else None
        return [self.converter.to_puzzle(item) for item in response["Items"]], next_cursor

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


def _encode_cursor(key: dict[str, str]) -> str:
    value = base64.urlsafe_b64encode(json.dumps(key, separators=(",", ":")).encode()).decode()
    return value.rstrip("=")


def _decode_cursor(cursor: str) -> dict[str, str]:
    try:
        if not cursor or len(cursor) > 256:
            raise ValueError
        padding = "=" * (-len(cursor) % 4)
        key = json.loads(base64.b64decode(cursor + padding, altchars=b"-_", validate=True))
        if not isinstance(key, dict) or set(key) != {"id"} or not isinstance(key["id"], str):
            raise ValueError
        UUID(key["id"])
        return key
    except (ValueError, TypeError) as e:
        raise InvalidPuzzleSummaryCursorError("Invalid puzzle summary cursor") from e
