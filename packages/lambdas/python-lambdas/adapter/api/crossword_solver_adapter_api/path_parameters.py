from uuid import UUID

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model


def uuid_path_parameter(event: APIGatewayProxyEventV2Model, name: str) -> UUID | None:
    value = (event.pathParameters or {}).get(name)
    try:
        return UUID(value) if value else None
    except ValueError:
        return None


def puzzle_id_path_parameter(event: APIGatewayProxyEventV2Model) -> UUID:
    return _required_uuid_path_parameter(event, "puzzleId")


def attempt_id_path_parameter(event: APIGatewayProxyEventV2Model) -> UUID:
    return _required_uuid_path_parameter(event, "attemptId")


def answer_id_path_parameter(event: APIGatewayProxyEventV2Model) -> str:
    value = (event.pathParameters or {}).get("answerId")
    if not value:
        raise ValueError("answerId path parameter is required")
    return value


def _required_uuid_path_parameter(event: APIGatewayProxyEventV2Model, name: str) -> UUID:
    value = (event.pathParameters or {}).get(name)
    if not value:
        raise ValueError(f"{name} path parameter is required")

    try:
        return UUID(value)
    except ValueError as error:
        raise ValueError(f"{name} path parameter must be a valid UUID") from error
