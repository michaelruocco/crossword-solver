import { parser } from '@aws-lambda-powertools/parser/middleware';
import { APIGatewayProxyEventV2Schema } from '@aws-lambda-powertools/parser/schemas';
import { z } from 'zod';
import middy from '@middy/core';
import { Tracer } from '@aws-lambda-powertools/tracer';
import { captureLambdaHandler } from '@aws-lambda-powertools/tracer/middleware';
import { injectLambdaContext } from '@aws-lambda-powertools/logger/middleware';
import { Logger } from '@aws-lambda-powertools/logger';
import { Metrics } from '@aws-lambda-powertools/metrics';
import { logMetrics } from '@aws-lambda-powertools/metrics/middleware';
import type { APIGatewayProxyResultV2 } from 'aws-lambda';

process.env.POWERTOOLS_METRICS_NAMESPACE = 'AutomaticAnswers';
process.env.POWERTOOLS_SERVICE_NAME = 'AutomaticAnswers';

const tracer = new Tracer();
const logger = new Logger();
const metrics = new Metrics();

export const automaticAnswersEventSchema = APIGatewayProxyEventV2Schema.extend({
  pathParameters: z.object({
    puzzleId: z.string().min(1),
    attemptId: z.string().min(1),
  }),
});

export const automaticAnswers = (
  event: z.infer<typeof automaticAnswersEventSchema>,
): APIGatewayProxyResultV2 => {
  logger.info('Received event', event);

  const { puzzleId, attemptId } = event.pathParameters;
  logger.info('Generating automatic answers for puzzle attempt', {
    puzzleId,
    attemptId,
  });

  return {
    statusCode: 201,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      id: attemptId,
      puzzle: { id: puzzleId },
    }),
  };
};

export const handler = middy()
  .use(captureLambdaHandler(tracer))
  .use(injectLambdaContext(logger))
  .use(logMetrics(metrics))
  .use(parser({ schema: automaticAnswersEventSchema }))
  .handler(automaticAnswers);
