import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.attempt_converter import AttemptConverter
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_adapter_repository.dynamodb_resource import create_dynamodb_resource
from crossword_solver_domain_use_case.attempt_creator import AttemptCreator
from crossword_solver_domain_use_case.attempt_finder import AttemptFinder
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_finder import PuzzleFinder
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError

logger: Logger = Logger(service="CreateAttempt")
tracer: Tracer = Tracer(service="CreateAttempt")

dynamodb = create_dynamodb_resource()
puzzle_repository = DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"], dynamodb=dynamodb)
attempt_repository = DynamoAttemptRepository(
    os.environ["ATTEMPTS_TABLE_NAME"],
    os.environ["PUZZLES_TABLE_NAME"],
    puzzle_repository,
    dynamodb=dynamodb,
)
puzzle_finder = PuzzleFinder(puzzle_repository)
attempt_creator = AttemptCreator(puzzle_finder, attempt_repository)
attempt_finder = AttemptFinder(attempt_repository)
attempt_converter = AttemptConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    puzzle_id = uuid_path_parameter(event, "puzzleId")
    if puzzle_id is None:
        return message_response(404, "Puzzle not found")

    try:
        attempt_id = attempt_creator.create(puzzle_id)
        attempt = attempt_finder.find_by_id(puzzle_id, attempt_id)
        response = attempt_converter.to_response(attempt).model_dump_json(by_alias=True)
        return json_response(201, response)
    except PuzzleNotFoundError:
        return message_response(404, "Puzzle not found")
    except AttemptNotFoundError:
        return message_response(404, "Attempt not found")
    except Exception as error:
        logger.exception(error)
        return message_response(500, "Internal server error")
