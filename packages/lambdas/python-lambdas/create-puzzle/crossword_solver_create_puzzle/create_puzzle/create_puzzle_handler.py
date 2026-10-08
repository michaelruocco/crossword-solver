import json
import os

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from crossword_solver_adapter_clue_extractor.bedrock_clue_extractor import BedrockClueExtractor
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_use_case.puzzle_creator import PuzzleCreator
from crossword_solver_image.default_image_downloader import DefaultImageDownloader

from .clue_response import ClueResponse
from .create_puzzle_request import CreatePuzzleRequest
from .puzzle_response import PuzzleResponse

os.environ["POWERTOOLS_METRICS_NAMESPACE"] = "CreatePuzzle"
os.environ["POWERTOOLS_SERVICE_NAME"] = "CreatePuzzle"

logger: Logger = Logger()
metrics: Metrics = Metrics()
tracer: Tracer = Tracer()

puzzle_creator = PuzzleCreator(
    clue_extractor=BedrockClueExtractor(model_id=os.environ["CLUE_EXTRACTOR_MODEL_ID"]),
    image_downloader=DefaultImageDownloader(),
)


def to_request(event: APIGatewayProxyEventV2Model) -> CreatePuzzleRequest:
    if not isinstance(event.body, str):
        raise ValueError("Request body is missing")

    return CreatePuzzleRequest.model_validate(json.loads(event.body))


def to_response(puzzle: Puzzle) -> PuzzleResponse:
    return PuzzleResponse(
        id=puzzle.id,
        name=puzzle.name,
        format=puzzle.format,
        hash=puzzle.hash,
        clues=[ClueResponse.from_clue(clue) for clue in puzzle.clues],
        createdAt=puzzle.created_at,
    )


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext) -> APIGatewayProxyResponseV2:
    logger.info("Received event", extra={"event": event.model_dump()})
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    try:
        request = to_request(event)
        puzzle = puzzle_creator.create(request.image_url)
        logger.info("Created puzzle", extra={"puzzle": puzzle})
        metrics.add_metric(name="SuccessCount", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 201,
            "headers": {"content-type": "application/json"},
            "body": to_response(puzzle).model_dump_json(by_alias=True),
        }
    except Exception as e:
        logger.exception(e)
        metrics.add_metric(name="ErrorCount", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"message": "Internal server error"}),
        }
