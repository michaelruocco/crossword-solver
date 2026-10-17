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
from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository
from crossword_solver_adapter_storage.s3_image_store import S3ImageStore
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError
from crossword_solver_domain_use_case.puzzle_upload_starter import PuzzleUploadStarter

logger: Logger = Logger(service="StartPuzzleUpload")
metrics: Metrics = Metrics(namespace="PuzzleImport", service="StartPuzzleUpload")
tracer: Tracer = Tracer(service="StartPuzzleUpload")

puzzle_upload_starter = PuzzleUploadStarter(
    repository=DynamoPuzzleImportRepository(os.environ["PUZZLE_IMPORTS_TABLE_NAME"]),
    upload_store=S3ImageStore(os.environ["PUZZLE_IMAGES_BUCKET_NAME"]),
)

event_converter = ApiGatewayEventConverter()
puzzle_import_converter = PuzzleImportConverter()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    try:
        request = event_converter.to_upload_request(event)
    except ValueError:
        # pydantic ValidationError and JSONDecodeError are both ValueErrors
        logger.warning("Invalid request", exc_info=True)
        metrics.add_metric(name="InvalidRequestCount", unit=MetricUnit.Count, value=1)
        return message_response(400, "Invalid request")

    try:
        puzzle_upload = puzzle_upload_starter.start(request.file_name)
        logger.info("Started puzzle upload", extra={"import_id": str(puzzle_upload.puzzle_import.id)})
        metrics.add_metric(name="SuccessCount", unit=MetricUnit.Count, value=1)
        return json_response(
            201,
            puzzle_import_converter.to_upload_response(puzzle_upload).model_dump_json(by_alias=True),
            {"location": puzzle_import_converter.to_location(puzzle_upload.puzzle_import)},
        )
    except InvalidImageError as e:
        logger.warning("Invalid image", exc_info=True)
        metrics.add_metric(name="InvalidImageCount", unit=MetricUnit.Count, value=1)
        return message_response(422, str(e))
    except Exception as e:
        logger.exception(e)
        metrics.add_metric(name="ErrorCount", unit=MetricUnit.Count, value=1)
        return message_response(500, "Internal server error")
