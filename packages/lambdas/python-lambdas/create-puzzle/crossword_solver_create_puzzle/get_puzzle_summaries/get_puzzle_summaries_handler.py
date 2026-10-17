import json
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.puzzle_summary_converter import PuzzleSummaryConverter
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.puzzle_summary_lister import PuzzleSummaryLister

logger: Logger = Logger(service="GetPuzzleSummaries")
tracer: Tracer = Tracer(service="GetPuzzleSummaries")

puzzle_summary_lister = PuzzleSummaryLister(DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"]))
puzzle_summary_converter = PuzzleSummaryConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    try:
        summaries = puzzle_summary_lister.list_all()
        body = json.dumps(
            [
                puzzle_summary_converter.to_response(summary).model_dump(by_alias=True, mode="json")
                for summary in summaries
            ]
        )
        return json_response(200, body)
    except Exception as e:
        logger.exception(e)
        return message_response(500, "Internal server error")
