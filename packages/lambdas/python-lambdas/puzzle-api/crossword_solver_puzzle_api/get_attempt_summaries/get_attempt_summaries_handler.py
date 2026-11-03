import json
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.attempt_summary_converter import AttemptSummaryConverter
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.attempt_lister import AttemptLister
from crossword_solver_domain_use_case.puzzle_finder import PuzzleFinder
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError

logger: Logger = Logger(service="GetAttemptSummaries")
tracer: Tracer = Tracer(service="GetAttemptSummaries")

puzzle_repository = DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"])
attempt_repository = DynamoAttemptRepository(
    os.environ["ATTEMPTS_TABLE_NAME"],
    os.environ["PUZZLES_TABLE_NAME"],
    puzzle_repository,
)
attempt_lister = AttemptLister(PuzzleFinder(puzzle_repository), attempt_repository)
attempt_summary_converter = AttemptSummaryConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    puzzle_id = uuid_path_parameter(event, "puzzleId")
    if puzzle_id is None:
        return message_response(404, "Puzzle not found")

    try:
        attempts = attempt_lister.list_by_puzzle_id(puzzle_id)
        summaries = [
            attempt_summary_converter.to_response(attempt).model_dump(by_alias=True, mode="json")
            for attempt in attempts
        ]
        return json_response(200, json.dumps(summaries))
    except PuzzleNotFoundError:
        return message_response(404, "Puzzle not found")
    except Exception as error:
        logger.exception(error)
        return message_response(500, "Internal server error")
