import json
from uuid import UUID

import boto3
from crossword_solver_domain_use_case.puzzle_import_queue import PuzzleImportQueue


class SqsPuzzleImportQueue(PuzzleImportQueue):
    def __init__(self, queue_url: str, client=None):
        self.queue_url = queue_url
        self.client = client or boto3.client("sqs")

    def send(self, import_id: UUID) -> None:
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps({"importId": str(import_id)}),
        )
