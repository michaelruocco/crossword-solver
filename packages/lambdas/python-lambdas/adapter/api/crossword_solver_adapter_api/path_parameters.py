from uuid import UUID

from aws_lambda_powertools import Logger
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
    return string_path_parameter(event, "answerId")


def clue_id_path_parameter(event: APIGatewayProxyEventV2Model) -> str:
    return string_path_parameter(event, "clueId")


def string_path_parameter(event: APIGatewayProxyEventV2Model, name: str) -> str:
    value = (event.pathParameters or {}).get(name)
    if not value:
        raise ValueError(f"{name} path parameter is required")
    return value


def attempt_answer_path_ids(event: APIGatewayProxyEventV2Model, logger: Logger) -> tuple[UUID, UUID]:
    try:
        puzzle_id = puzzle_id_path_parameter(event)
    except ValueError as error:
        logger.error("Invalid puzzle id path parameter", exc_info=True)
        raise ValueError("Invalid puzzle id") from error

    try:
        attempt_id = attempt_id_path_parameter(event)
    except ValueError as error:
        logger.error("Invalid attempt id path parameter", exc_info=True)
        raise ValueError("Invalid attempt id") from error

    return puzzle_id, attempt_id


def _required_uuid_path_parameter(event: APIGatewayProxyEventV2Model, name: str) -> UUID:
    value = (event.pathParameters or {}).get(name)
    if not value:
        raise ValueError(f"{name} path parameter is required")

    try:
        return UUID(value)
    except ValueError as error:
        raise ValueError(f"{name} path parameter must be a valid UUID") from error
