import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_api.puzzle_import_converter import PuzzleImportConverter
from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository
from crossword_solver_domain_use_case.puzzle_import_finder import PuzzleImportFinder
from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError

logger: Logger = Logger(service="GetPuzzleImport")
tracer: Tracer = Tracer(service="GetPuzzleImport")

puzzle_import_finder = PuzzleImportFinder(DynamoPuzzleImportRepository(os.environ["PUZZLE_IMPORTS_TABLE_NAME"]))

puzzle_import_converter = PuzzleImportConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    import_id = uuid_path_parameter(event, "importId")
    if import_id is None:
        return message_response(404, "Puzzle import not found")

    try:
        puzzle_import = puzzle_import_finder.find_by_id(import_id)
        return json_response(200, puzzle_import_converter.to_response(puzzle_import).model_dump_json(by_alias=True))
    except PuzzleImportNotFoundError:
        return message_response(404, "Puzzle import not found")
    except Exception as e:
        logger.exception(e)
        return message_response(500, "Internal server error")
