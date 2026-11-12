import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.answer_converter import AnswerConverter
from crossword_solver_adapter_api.api_gateway_event_converter import ApiGatewayEventConverter
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.attempt_converter import AttemptConverter
from crossword_solver_adapter_api.path_parameters import uuid_path_parameter
from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_adapter_repository.dynamodb_resource import create_dynamodb_resource
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_use_case.attempt_answer_saver import AttemptAnswerSaver
from crossword_solver_domain_use_case.attempt_finder import AttemptFinder
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError

logger: Logger = Logger(service="UpdateAttemptAnswer")
tracer: Tracer = Tracer(service="UpdateAttemptAnswer")

dynamodb = create_dynamodb_resource()
puzzle_repository = DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"], dynamodb=dynamodb)
attempt_repository = DynamoAttemptRepository(
    os.environ["ATTEMPTS_TABLE_NAME"],
    os.environ["PUZZLES_TABLE_NAME"],
    puzzle_repository,
    dynamodb=dynamodb,
)
attempt_finder = AttemptFinder(attempt_repository)
attempt_answer_saver = AttemptAnswerSaver(attempt_finder, attempt_repository)
event_converter = ApiGatewayEventConverter()
answer_converter = AnswerConverter()
attempt_converter = AttemptConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    puzzle_id = uuid_path_parameter(event, "puzzleId")
    if puzzle_id is None:
        return message_response(404, "Puzzle not found")

    attempt_id = uuid_path_parameter(event, "attemptId")
    if attempt_id is None:
        return message_response(404, "Attempt not found")

    try:
        answer = answer_converter.to_domain(event_converter.to_answer_request(event))
    except ValueError:
        logger.warning("Invalid answer request", exc_info=True)
        return message_response(400, "Invalid answer request")

    try:
        attempt_answer_saver.save(puzzle_id, attempt_id, answer)
        attempt = attempt_finder.find_by_id(puzzle_id, attempt_id)
        return json_response(200, attempt_converter.to_response(attempt).model_dump_json(by_alias=True))
    except AttemptNotFoundError:
        return message_response(404, "Attempt not found")
    except PuzzleNotFoundError:
        return message_response(404, "Puzzle not found")
    except ClueNotFoundForIdError:
        return message_response(404, "Clue not found")
    except Exception as error:
        logger.exception(error)
        return message_response(500, "Internal server error")
