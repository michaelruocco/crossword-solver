from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.path_parameters import (
    answer_id_path_parameter,
    attempt_id_path_parameter,
    puzzle_id_path_parameter,
)

from ..attempt_answer_dependencies import answer_converter, attempt_answer_service, attempt_converter
from ..attempt_answer_error_handler import attempt_answer_error_response

logger: Logger = Logger(service="DeleteAttemptAnswer")
tracer: Tracer = Tracer(service="DeleteAttemptAnswer")


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})

    try:
        puzzle_id = puzzle_id_path_parameter(event)
    except ValueError:
        logger.error("Invalid puzzle id path parameter", exc_info=True)
        return message_response(400, "Invalid puzzle id")

    try:
        attempt_id = attempt_id_path_parameter(event)
    except ValueError:
        logger.error("Invalid attempt id path parameter", exc_info=True)
        return message_response(400, "Invalid attempt id")

    try:
        domain_answer_id = answer_converter.to_id(answer_id_path_parameter(event))
    except ValueError:
        logger.warning("Invalid answer id", exc_info=True)
        return message_response(400, "Invalid answer id")

    try:
        attempt = attempt_answer_service.delete_answer(puzzle_id, attempt_id, domain_answer_id)
        return json_response(200, attempt_converter.to_response(attempt).model_dump_json(by_alias=True))
    except Exception as error:
        return attempt_answer_error_response(error, logger)
