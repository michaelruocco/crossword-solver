from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.path_parameters import attempt_answer_path_ids, clue_id_path_parameter

from ..attempt_answer_error_handler import attempt_answer_error_response
from ..candidate_answer_dependencies import (
    answer_converter,
    attempt_candidate_loader,
    candidate_answers_converter,
)

logger: Logger = Logger(service="GetCandidateAnswers")
tracer: Tracer = Tracer(service="GetCandidateAnswers")


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    try:
        puzzle_id, attempt_id = attempt_answer_path_ids(event, logger)
    except ValueError as error:
        return message_response(400, str(error))

    try:
        clue_id = answer_converter.to_id(clue_id_path_parameter(event))
    except ValueError:
        logger.warning("Invalid clue id", exc_info=True)
        return message_response(400, "Invalid clue id")

    try:
        candidates = attempt_candidate_loader.load_candidates(puzzle_id, attempt_id, clue_id)
        response = candidate_answers_converter.to_response(candidates)
        return json_response(200, response.model_dump_json(by_alias=True))
    except Exception as error:
        return attempt_answer_error_response(error, logger)
