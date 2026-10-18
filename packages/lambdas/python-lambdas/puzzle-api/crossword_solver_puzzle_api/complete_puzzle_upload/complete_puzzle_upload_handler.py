import os

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging.utils import copy_config_to_registered_loggers
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import S3Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from crossword_solver_adapter_queue.sqs_puzzle_import_queue import SqsPuzzleImportQueue
from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository
from crossword_solver_adapter_storage.s3_image_store import import_id_from_upload_key
from crossword_solver_domain_use_case.puzzle_upload_completer import PuzzleUploadCompleter

logger: Logger = Logger(service="CompletePuzzleUpload")
metrics: Metrics = Metrics(namespace="PuzzleImport", service="CompletePuzzleUpload")
tracer: Tracer = Tracer(service="CompletePuzzleUpload")

copy_config_to_registered_loggers(source_logger=logger, include={"crossword_solver_domain_use_case"})

puzzle_upload_completer = PuzzleUploadCompleter(
    repository=DynamoPuzzleImportRepository(os.environ["PUZZLE_IMPORTS_TABLE_NAME"]),
    queue=SqsPuzzleImportQueue(os.environ["PUZZLE_IMPORT_QUEUE_URL"]),
)


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=S3Model)
def lambda_handler(event: S3Model, context: LambdaContext) -> None:
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    # Errors are left to propagate so Lambda retries the notification.
    for record in event.Records:
        # S3Model rejects object created records without an object, so this only narrows the type.
        assert record.s3.object is not None
        import_id = import_id_from_upload_key(record.s3.object.key)
        logger.info("Completing puzzle upload", extra={"import_id": str(import_id)})
        puzzle_upload_completer.complete(import_id)
