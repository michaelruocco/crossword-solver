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
import { randomUUID } from 'node:crypto';

process.env.POWERTOOLS_METRICS_NAMESPACE = 'CreateAttempt';
process.env.POWERTOOLS_SERVICE_NAME = 'CreateAttempt';

const tracer = new Tracer();
const logger = new Logger();
const metrics = new Metrics();

export const createAttemptEventSchema = APIGatewayProxyEventV2Schema.extend({
  pathParameters: z.object({
    puzzleId: z.string().min(1),
  }),
});

export const createAttempt = async (
  event: z.infer<typeof createAttemptEventSchema>,
): Promise<APIGatewayProxyResultV2> => {
  logger.info('Received event', event);

  const { puzzleId } = event.pathParameters;
  logger.info('Creating attempt for puzzle', { puzzleId });

  return {
    statusCode: 201,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      id: randomUUID(),
      puzzle: { id: puzzleId },
    }),
  };
};

export const handler = middy()
  .use(captureLambdaHandler(tracer))
  .use(injectLambdaContext(logger))
  .use(logMetrics(metrics))
  .use(parser({ schema: createAttemptEventSchema }))
  .handler(createAttempt);
