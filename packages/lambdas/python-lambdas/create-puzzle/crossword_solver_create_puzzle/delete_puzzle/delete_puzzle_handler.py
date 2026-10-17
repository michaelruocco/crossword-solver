import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import message_response, no_content_response
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.puzzle_deleter import PuzzleDeleter

logger: Logger = Logger(service="DeletePuzzle")
tracer: Tracer = Tracer(service="DeletePuzzle")

puzzle_deleter = PuzzleDeleter(DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"]))


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    puzzle_id = uuid_path_parameter(event, "puzzleId")
    if puzzle_id is None:
        return message_response(404, "Puzzle not found")

    try:
        puzzle_deleter.delete(puzzle_id)
        return no_content_response()
    except Exception as e:
        logger.exception(e)
        return message_response(500, "Internal server error")
