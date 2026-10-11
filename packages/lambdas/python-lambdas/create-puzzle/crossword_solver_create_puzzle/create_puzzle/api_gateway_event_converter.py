import json

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from .create_puzzle_request import CreatePuzzleRequest


class ApiGatewayEventConverter:
    def to_request(self, event: APIGatewayProxyEventV2Model) -> CreatePuzzleRequest:
        if not isinstance(event.body, str):
            raise ValueError("Request body is missing")

        return CreatePuzzleRequest.model_validate(json.loads(event.body))
