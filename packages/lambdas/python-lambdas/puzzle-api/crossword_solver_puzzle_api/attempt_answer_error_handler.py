from aws_lambda_powertools import Logger
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import message_response
from crossword_solver_domain_entities.clue_not_found_for_id_error import ClueNotFoundForIdError
from crossword_solver_domain_entities.invalid_answer_error import InvalidAnswerError
from crossword_solver_domain_use_case.attempt_not_found_error import AttemptNotFoundError
from crossword_solver_domain_use_case.puzzle_not_found_error import PuzzleNotFoundError


def attempt_answer_error_response(error: Exception, logger: Logger) -> APIGatewayProxyResponseV2:
    if isinstance(error, AttemptNotFoundError):
        return message_response(404, "Attempt not found")
    if isinstance(error, PuzzleNotFoundError):
        return message_response(404, "Puzzle not found")
    if isinstance(error, ClueNotFoundForIdError):
        return message_response(404, "Clue not found")
    if isinstance(error, InvalidAnswerError):
        return message_response(400, "Invalid answer")

    logger.exception(error)
    return message_response(500, "Internal server error")
