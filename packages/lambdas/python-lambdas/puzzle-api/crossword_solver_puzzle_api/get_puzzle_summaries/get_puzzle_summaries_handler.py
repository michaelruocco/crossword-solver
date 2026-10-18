import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_gateway_event_converter import ApiGatewayEventConverter
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.puzzle_summary_converter import PuzzleSummaryConverter
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.invalid_puzzle_summary_cursor_error import InvalidPuzzleSummaryCursorError
from crossword_solver_domain_use_case.puzzle_summary_lister import PuzzleSummaryLister

logger: Logger = Logger(service="GetPuzzleSummaries")
tracer: Tracer = Tracer(service="GetPuzzleSummaries")

puzzle_summary_lister = PuzzleSummaryLister(DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"]))
puzzle_summary_converter = PuzzleSummaryConverter()
event_converter = ApiGatewayEventConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    try:
        query = event_converter.to_puzzle_summary_query(event)
    except ValueError:
        return message_response(400, "Invalid request")

    try:
        page = puzzle_summary_lister.list_page(query.limit, query.cursor)
        body = puzzle_summary_converter.to_page_response(page).model_dump_json(by_alias=True)
        return json_response(200, body)
    except InvalidPuzzleSummaryCursorError:
        return message_response(400, "Invalid cursor")
    except Exception as e:
        logger.exception(e)
        return message_response(500, "Internal server error")
