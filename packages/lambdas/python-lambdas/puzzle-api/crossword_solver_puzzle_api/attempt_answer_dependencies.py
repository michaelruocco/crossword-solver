import os

from crossword_solver_adapter_api.answer_converter import AnswerConverter
from crossword_solver_adapter_api.api_gateway_event_converter import ApiGatewayEventConverter
from crossword_solver_adapter_api.attempt_converter import AttemptConverter
from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_adapter_repository.dynamodb_resource import create_dynamodb_resource
from crossword_solver_domain_use_case.attempt_answer_service import AttemptAnswerService
from crossword_solver_domain_use_case.attempt_finder import AttemptFinder

dynamodb = create_dynamodb_resource()
puzzle_repository = DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"], dynamodb=dynamodb)
attempt_repository = DynamoAttemptRepository(
    os.environ["ATTEMPTS_TABLE_NAME"],
    os.environ["PUZZLES_TABLE_NAME"],
    puzzle_repository,
    dynamodb=dynamodb,
)
attempt_finder = AttemptFinder(attempt_repository)
attempt_answer_service = AttemptAnswerService(attempt_finder, attempt_repository)
answer_converter = AnswerConverter()
attempt_converter = AttemptConverter()
event_converter = ApiGatewayEventConverter()
