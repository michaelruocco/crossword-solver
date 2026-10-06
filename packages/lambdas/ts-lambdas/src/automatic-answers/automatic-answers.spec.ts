import { describe, expect, it } from 'vitest';
import {
  automaticAnswers,
  automaticAnswersEventSchema,
} from './automatic-answers.js';
import type { z } from 'zod';

const routeKey =
  'POST /v1/puzzles/{puzzleId}/attempts/{attemptId}/automatic-answers';

const buildEvent = (
  puzzleId: string,
  attemptId: string,
): z.infer<typeof automaticAnswersEventSchema> => ({
  version: '2.0',
  routeKey,
  rawPath: `/v1/puzzles/${puzzleId}/attempts/${attemptId}/automatic-answers`,
  rawQueryString: '',
  headers: { 'content-type': 'application/json' },
  pathParameters: { puzzleId, attemptId },
  requestContext: {
    accountId: '123456789012',
    apiId: 'api-id',
    domainName: 'api-id.execute-api.eu-west-2.amazonaws.com',
    domainPrefix: 'api-id',
    http: {
      method: 'POST',
      path: `/v1/puzzles/${puzzleId}/attempts/${attemptId}/automatic-answers`,
      protocol: 'HTTP/1.1',
      sourceIp: '127.0.0.1',
      userAgent: 'agent',
    },
    requestId: 'request-id',
    routeKey,
    stage: '$default',
    time: '01/Jan/2024:00:00:00 +0000',
    timeEpoch: 1704067200000,
  },
  isBase64Encoded: false,
});

describe('automaticAnswers', () => {
  it('returns a new id with the puzzle and attempt ids from the path', async () => {
    const result = await automaticAnswers(
      buildEvent('puzzle-123', 'attempt-456'),
    );

    expect(result).toMatchObject({ statusCode: 201 });

    const body = JSON.parse((result as { body: string }).body) as Record<
      string,
      unknown
    >;

    expect(Object.keys(body).sort()).toEqual(['attempt', 'id', 'puzzle']);
    expect(body['id']).toMatch('attempt-456');
    expect(body['puzzle']).toEqual({ id: 'puzzle-123' });
  });

  it('rejects an event missing the attemptId path parameter', () => {
    const event = {
      ...buildEvent('puzzle-123', 'attempt-456'),
      pathParameters: { puzzleId: 'puzzle-123' },
    };

    expect(automaticAnswersEventSchema.safeParse(event).success).toBe(false);
  });
});
