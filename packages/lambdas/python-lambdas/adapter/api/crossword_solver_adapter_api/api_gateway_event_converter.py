import json

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model

from .create_puzzle_request import CreatePuzzleRequest
from .create_puzzle_upload_request import CreatePuzzleUploadRequest
from .puzzle_summary_query import PuzzleSummaryQuery


class ApiGatewayEventConverter:
    def to_request(self, event: APIGatewayProxyEventV2Model) -> CreatePuzzleRequest:
        return CreatePuzzleRequest.model_validate(_to_json(event))

    def to_upload_request(self, event: APIGatewayProxyEventV2Model) -> CreatePuzzleUploadRequest:
        return CreatePuzzleUploadRequest.model_validate(_to_json(event))

    def to_puzzle_summary_query(self, event: APIGatewayProxyEventV2Model) -> PuzzleSummaryQuery:
        return PuzzleSummaryQuery.model_validate(event.queryStringParameters or {})


def _to_json(event: APIGatewayProxyEventV2Model) -> object:
    if not isinstance(event.body, str):
        raise ValueError("Request body is missing")

    return json.loads(event.body)
