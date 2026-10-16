import os

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_api.api_gateway_event_converter import ApiGatewayEventConverter
from crossword_solver_adapter_api.api_response import json_response, message_response
from crossword_solver_adapter_api.puzzle_import_converter import PuzzleImportConverter
from crossword_solver_adapter_queue.sqs_puzzle_import_queue import SqsPuzzleImportQueue
from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository
from crossword_solver_adapter_storage.s3_image_store import S3ImageStore
from crossword_solver_adapter_web.web_image_fetcher import WebImageFetcher
from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_import_starter import PuzzleImportStarter
from crossword_solver_domain_use_case.puzzle_url_import_starter import PuzzleUrlImportStarter

logger: Logger = Logger(service="StartPuzzleImport")
metrics: Metrics = Metrics(namespace="PuzzleImport", service="StartPuzzleImport")
tracer: Tracer = Tracer(service="StartPuzzleImport")

puzzle_url_import_starter = PuzzleUrlImportStarter(
    fetcher=WebImageFetcher(),
    store=S3ImageStore(os.environ["PUZZLE_IMAGES_BUCKET_NAME"]),
    starter=PuzzleImportStarter(
        repository=DynamoPuzzleImportRepository(os.environ["PUZZLE_IMPORTS_TABLE_NAME"]),
        queue=SqsPuzzleImportQueue(os.environ["PUZZLE_IMPORT_QUEUE_URL"]),
    ),
)

event_converter = ApiGatewayEventConverter()
puzzle_import_converter = PuzzleImportConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    try:
        request = event_converter.to_request(event)
    except ValueError:
        # pydantic ValidationError and JSONDecodeError are both ValueErrors
        logger.warning("Invalid request", exc_info=True)
        metrics.add_metric(name="InvalidRequestCount", unit=MetricUnit.Count, value=1)
        return message_response(400, "Invalid request")

    try:
        puzzle_import = puzzle_url_import_starter.start(request.image_url)
        logger.info("Started puzzle import", extra={"import_id": str(puzzle_import.id)})
        metrics.add_metric(name="SuccessCount", unit=MetricUnit.Count, value=1)
        return json_response(
            202,
            puzzle_import_converter.to_response(puzzle_import).model_dump_json(by_alias=True),
            {"location": puzzle_import_converter.to_location(puzzle_import)},
        )
    except InvalidImageError as e:
        # These messages come from our own rules, so the client can act on them.
        logger.warning("Invalid image", exc_info=True)
        metrics.add_metric(name="InvalidImageCount", unit=MetricUnit.Count, value=1)
        return message_response(422, str(e))
    except ImageError:
        # One generic message for every fetch failure, so the response can't be used to probe other hosts.
        logger.warning("Failed to retrieve image", exc_info=True)
        metrics.add_metric(name="ImageRetrievalFailureCount", unit=MetricUnit.Count, value=1)
        return message_response(422, "Unable to retrieve image from the given URL")
    except Exception as e:
        logger.exception(e)
        metrics.add_metric(name="ErrorCount", unit=MetricUnit.Count, value=1)
        return message_response(500, "Internal server error")
