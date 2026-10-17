import json

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from .create_puzzle_request import CreatePuzzleRequest
from .create_puzzle_upload_request import CreatePuzzleUploadRequest


class ApiGatewayEventConverter:
    def to_request(self, event: APIGatewayProxyEventV2Model) -> CreatePuzzleRequest:
        return CreatePuzzleRequest.model_validate(_to_json(event))

    def to_upload_request(self, event: APIGatewayProxyEventV2Model) -> CreatePuzzleUploadRequest:
        return CreatePuzzleUploadRequest.model_validate(_to_json(event))


def _to_json(event: APIGatewayProxyEventV2Model) -> object:
    if not isinstance(event.body, str):
        raise ValueError("Request body is missing")

    return json.loads(event.body)
