from unittest.mock import patch

from crossword_solver_adapter_repository import dynamodb_resource


def test_dynamodb_resource_uses_bounded_timeouts_and_retries():
    with (
        patch.object(dynamodb_resource, "Config") as config,
        patch.object(dynamodb_resource.boto3, "resource") as resource,
    ):
        result = dynamodb_resource.create_dynamodb_resource()

    config.assert_called_once_with(
        connect_timeout=1,
        read_timeout=2,
        retries={"mode": "standard", "total_max_attempts": 2},
    )
    resource.assert_called_once_with("dynamodb", config=config.return_value)
    assert result is resource.return_value
