import os

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventV2Model
from aws_lambda_powertools.utilities.typing import LambdaContext

os.environ["POWERTOOLS_METRICS_NAMESPACE"] = "CreatePuzzle"
os.environ["POWERTOOLS_SERVICE_NAME"] = "CreatePuzzle"

logger: Logger = Logger()
metrics: Metrics = Metrics()
tracer: Tracer = Tracer()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
@event_parser(model=APIGatewayProxyEventV2Model)
def lambda_handler(event: APIGatewayProxyEventV2Model, context: LambdaContext):
    logger.info("Received event", extra={"event": event.model_dump()})
    metrics.add_metric(name="InvocationCount", unit=MetricUnit.Count, value=1)

    try:
        # TODO: Implement
        metrics.add_metric(name="SuccessCount", unit=MetricUnit.Count, value=1)
        # TODO: Implement success response if required
    except Exception as e:
        logger.exception(e)
        metrics.add_metric(name="ErrorCount", unit=MetricUnit.Count, value=1)
        # TODO: Implement error response if required
