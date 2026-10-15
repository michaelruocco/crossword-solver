from uuid import UUID

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model


def uuid_path_parameter(event: APIGatewayProxyEventV2Model, name: str) -> UUID | None:
    value = (event.pathParameters or {}).get(name)
    try:
        return UUID(value) if value else None
    except ValueError:
        return None
