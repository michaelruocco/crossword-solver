import os

from crossword_solver_adapter_answer_finder.bedrock_answer_finder import BedrockAnswerFinder
from crossword_solver_adapter_api.answer_converter import AnswerConverter
from crossword_solver_adapter_api.candidate_answers_converter import CandidateAnswersConverter
from crossword_solver_adapter_repository.dynamo_attempt_repository import DynamoAttemptRepository
from crossword_solver_adapter_repository.dynamo_candidate_repository import DynamoCandidateRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_adapter_repository.dynamodb_resource import create_dynamodb_resource
from crossword_solver_domain_use_case.attempt_candidate_loader import AttemptCandidateLoader
from crossword_solver_domain_use_case.attempt_finder import AttemptFinder
from crossword_solver_domain_use_case.candidate_loader import CandidateLoader

dynamodb = create_dynamodb_resource()
puzzle_repository = DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"], dynamodb=dynamodb)
attempt_repository = DynamoAttemptRepository(
    os.environ["ATTEMPTS_TABLE_NAME"],
    os.environ["PUZZLES_TABLE_NAME"],
    puzzle_repository,
    dynamodb=dynamodb,
)
candidate_repository = DynamoCandidateRepository(os.environ["CANDIDATES_TABLE_NAME"], dynamodb=dynamodb)
attempt_finder = AttemptFinder(attempt_repository)
candidate_loader = CandidateLoader(
    BedrockAnswerFinder(model_id=os.environ.get("ANSWER_FINDER_MODEL_ID")),
    candidate_repository,
)
attempt_candidate_loader = AttemptCandidateLoader(attempt_finder, candidate_loader)
answer_converter = AnswerConverter()
candidate_answers_converter = CandidateAnswersConverter()
