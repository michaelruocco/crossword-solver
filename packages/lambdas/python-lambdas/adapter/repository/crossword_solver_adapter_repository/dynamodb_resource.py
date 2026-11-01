import boto3
from botocore.config import Config


def create_dynamodb_resource():
    config = Config(
        connect_timeout=1,
        read_timeout=2,
        retries={"mode": "standard", "total_max_attempts": 2},
    )
    return boto3.resource("dynamodb", config=config)
