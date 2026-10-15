import os

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging.utils import copy_config_to_registered_loggers
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import envelopes, event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from crossword_solver_adapter_clue_extractor.bedrock_clue_extractor import BedrockClueExtractor
from crossword_solver_adapter_grid_extractor.cell_factory import CellFactory
from crossword_solver_adapter_grid_extractor.default_grid_extractor import DefaultGridExtractor
from crossword_solver_adapter_grid_extractor.number_detector import NumberDetector
from crossword_solver_adapter_repository.dynamo_puzzle_import_repository import DynamoPuzzleImportRepository
from crossword_solver_adapter_repository.dynamo_puzzle_repository import DynamoPuzzleRepository
from crossword_solver_domain_use_case.puzzle_creator import PuzzleCreator
from crossword_solver_domain_use_case.puzzle_import_processor import PuzzleImportProcessor
from crossword_solver_image.default_image_downloader import DefaultImageDownloader

from .puzzle_import_message import PuzzleImportMessage

logger: Logger = Logger(service="ProcessPuzzleImport")
metrics: Metrics = Metrics(namespace="PuzzleImport", service="ProcessPuzzleImport")
tracer: Tracer = Tracer(service="ProcessPuzzleImport")

# Library modules use standard logging, which Lambda doesn't output unless given the Powertools handler.
copy_config_to_registered_loggers(
    source_logger=logger,
    include={
        "crossword_solver_adapter_clue_extractor",
        "crossword_solver_adapter_grid_extractor",
        "crossword_solver_domain_use_case",
        "crossword_solver_image",
    },
)

puzzle_import_processor = PuzzleImportProcessor(
    repository=DynamoPuzzleImportRepository(os.environ["PUZZLE_IMPORTS_TABLE_NAME"]),
    creator=PuzzleCreator(
        clue_extractor=BedrockClueExtractor(model_id=os.environ["CLUE_EXTRACTOR_MODEL_ID"]),
        grid_extractor=DefaultGridExtractor(CellFactory(NumberDetector(os.environ["TESSDATA_PREFIX"]))),
        image_downloader=DefaultImageDownloader(),
        repository=DynamoPuzzleRepository(os.environ["PUZZLES_TABLE_NAME"]),
    ),
)


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=PuzzleImportMessage, envelope=envelopes.SqsEnvelope)
def lambda_handler(event: list[PuzzleImportMessage], context: LambdaContext) -> None:
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    # Errors are left to propagate so the queue retries the message and eventually moves it to the dead-letter queue.
    for message in event:
        logger.info("Processing puzzle import", extra={"import_id": str(message.import_id)})
        puzzle_import_processor.process(message.import_id)
