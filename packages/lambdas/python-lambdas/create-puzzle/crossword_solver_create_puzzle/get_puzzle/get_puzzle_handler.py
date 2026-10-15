import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_api.puzzle_converter import PuzzleConverter
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.puzzle_finder import PuzzleFinder
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError

logger: Logger = Logger(service="GetPuzzle")
tracer: Tracer = Tracer(service="GetPuzzle")

puzzle_finder = PuzzleFinder(DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"]))

puzzle_converter = PuzzleConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    puzzle_id = uuid_path_parameter(event, "puzzleId")
    if puzzle_id is None:
        return message_response(404, "Puzzle not found")

    try:
        puzzle = puzzle_finder.find_by_id(puzzle_id)
        return json_response(200, puzzle_converter.to_response(puzzle).model_dump_json(by_alias=True))
    except PuzzleNotFoundError:
        return message_response(404, "Puzzle not found")
    except Exception as e:
        logger.exception(e)
        return message_response(500, "Internal server error")
