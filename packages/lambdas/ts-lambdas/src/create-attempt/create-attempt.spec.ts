import { describe, expect, it } from 'vitest';
import { createAttempt, createAttemptEventSchema } from './create-attempt.js';
import type { z } from 'zod';

const buildEvent = (
  puzzleId: string,
): z.infer<typeof createAttemptEventSchema> => ({
  version: '2.0',
  routeKey: 'POST /v1/puzzles/{puzzleId}/attempts',
  rawPath: `/v1/puzzles/${puzzleId}/attempts`,
  rawQueryString: '',
  headers: { 'content-type': 'application/json' },
  pathParameters: { puzzleId },
  requestContext: {
    accountId: '123456789012',
    apiId: 'api-id',
    domainName: 'api-id.execute-api.eu-west-2.amazonaws.com',
    domainPrefix: 'api-id',
    http: {
      method: 'POST',
      path: `/v1/puzzles/${puzzleId}/attempts`,
      protocol: 'HTTP/1.1',
      sourceIp: '127.0.0.1',
      userAgent: 'agent',
    },
    requestId: 'request-id',
    routeKey: 'POST /v1/puzzles/{puzzleId}/attempts',
    stage: '$default',
    time: '01/Jan/2024:00:00:00 +0000',
    timeEpoch: 1704067200000,
  },
  isBase64Encoded: false,
});

const uuidPattern =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

describe('createAttempt', () => {
  it('returns a new attempt id and the puzzle id from the path', async () => {
    const result = await createAttempt(buildEvent('puzzle-123'));

    expect(result).toMatchObject({ statusCode: 201 });

    const body = JSON.parse((result as { body: string }).body) as Record<
      string,
      unknown
    >;

    expect(Object.keys(body).sort()).toEqual(['id', 'puzzle']);
    expect(body['id']).toMatch(uuidPattern);
    expect(body['puzzle']).toEqual({ id: 'puzzle-123' });
  });

  it('rejects an event without a puzzleId path parameter', () => {
    const event = { ...buildEvent('puzzle-123'), pathParameters: {} };

    expect(createAttemptEventSchema.safeParse(event).success).toBe(false);
  });
});
