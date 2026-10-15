import json
from uuid import uuid4

import boto3
import pytest
from moto import mock_aws

from crossword_solver_adapter_queue.sqs_puzzle_import_queue import SqsPuzzleImportQueue


@pytest.fixture
def sqs():
    with mock_aws():
        yield boto3.client("sqs", region_name="eu-west-2")


@pytest.fixture
def queue_url(sqs) -> str:
    return sqs.create_queue(QueueName="puzzle-imports")["QueueUrl"]


def test_send_puts_import_id_message_on_queue(sqs, queue_url):
    import_id = uuid4()
    queue = SqsPuzzleImportQueue(queue_url, client=sqs)

    queue.send(import_id)

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10).get("Messages", [])
    assert [json.loads(message["Body"]) for message in messages] == [{"importId": str(import_id)}]
