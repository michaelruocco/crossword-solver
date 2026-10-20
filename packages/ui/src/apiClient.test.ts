import { afterEach, expect, test, vi } from 'vitest'
import { ApiClient } from './apiClient'

afterEach(() => vi.unstubAllGlobals())

test('starts an upload and returns the signed form and import location', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ id: 'import-1', upload: { url: 'https://bucket.test', fields: { key: 'uploads/key' } } }), {
      status: 201,
      headers: { location: '/v1/puzzles/imports/import-1' },
    }),
  )
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  const result = await client.startPuzzleUpload('puzzle.png')

  expect(fetchMock).toHaveBeenCalledWith('https://api.test/v1/puzzles/uploads', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ fileName: 'puzzle.png' }),
    signal: undefined,
  })
  expect(result).toEqual({
    upload: { url: 'https://bucket.test', fields: { key: 'uploads/key' } },
    location: '/v1/puzzles/imports/import-1',
  })
})

test('uploads a multipart form with all signed fields and the file last', async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('')
  const file = new File(['image'], 'puzzle.png', { type: 'image/png' })

  await client.uploadPuzzleFile(
    { url: 'https://bucket.test', fields: { key: 'uploads/key', policy: 'signed-policy' } },
    file,
  )

  const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit]
  const body = options.body as FormData
  expect(url).toBe('https://bucket.test')
  expect(body.get('key')).toBe('uploads/key')
  expect(body.get('policy')).toBe('signed-policy')
  expect(body.get('file')).toBe(file)
})

test('waits for a completed import and propagates failed imports', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'PENDING' }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'COMPLETE', puzzleId: 'puzzle-1' }), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  vi.stubGlobal('setTimeout', (callback: TimerHandler) => {
    if (typeof callback === 'function') callback()
    return 1
  })
  const client = new ApiClient('https://api.test')

  const result = await client.waitForPuzzleImport('/v1/puzzles/imports/import-1')

  expect(result.status).toBe('COMPLETE')
  expect(fetchMock).toHaveBeenCalledTimes(2)
})

test('deletes a puzzle by id', async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await client.deletePuzzle('puzzle-1')

  expect(fetchMock).toHaveBeenCalledWith('https://api.test/v1/puzzles/puzzle-1', {
    method: 'DELETE',
    signal: undefined,
  })
})

test('loads a summary page with the requested limit and cursor', async () => {
  const page = { summaries: [], nextCursor: null }
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(page), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test///')

  await expect(client.getPuzzleSummaryPage({ limit: 25, cursor: 'cursor-1' })).resolves.toEqual(page)

  const [requestUrl] = fetchMock.mock.calls[0] as [URL]
  expect(requestUrl.origin).toBe('https://api.test')
  expect(requestUrl.searchParams.get('limit')).toBe('25')
  expect(requestUrl.searchParams.get('cursor')).toBe('cursor-1')
})

test('loads all summary pages and rejects a repeated cursor', async () => {
  const first = { id: 'one', name: 'First', createdAt: '2026-10-18', clueCount: 10 }
  const second = { id: 'two', name: 'Second', createdAt: '2026-10-17', clueCount: 12 }
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ summaries: [first], nextCursor: 'next' }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ summaries: [second], nextCursor: null }), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await expect(client.getAllPuzzleSummaries()).resolves.toEqual([first, second])
  expect(new URL(fetchMock.mock.calls[1][0] as URL).searchParams.get('cursor')).toBe('next')

  fetchMock
    .mockResolvedValueOnce(new Response(JSON.stringify({ summaries: [], nextCursor: 'repeat' }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ summaries: [], nextCursor: 'repeat' }), { status: 200 }))
  await expect(client.getAllPuzzleSummaries()).rejects.toThrow('Puzzle API returned a repeated pagination cursor.')
})

test('uses a generated import location when the response has no location header', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ id: 'import /1', upload: { url: 'https://bucket.test', fields: {} } }), { status: 201 }),
  )
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await expect(client.startPuzzleUpload('puzzle.png')).resolves.toMatchObject({
    location: '/v1/puzzles/imports/import%20%2F1',
  })
})

test('uses API error messages and falls back when an error response is not JSON', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ message: 'Not available' }), { status: 503 }))
    .mockResolvedValueOnce(new Response('not json', { status: 502 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({}), { status: 502 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ message: '' }), { status: 502 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ message: 42 }), { status: 502 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await expect(client.getPuzzleSummaryPage()).rejects.toThrow('Puzzle API returned 503 while loading summaries.')
  await expect(client.getPuzzleImport('/v1/imports/one')).rejects.toThrow('Unable to read puzzle import status.')
  await expect(client.getPuzzleImport('/v1/imports/two')).rejects.toThrow('Unable to read puzzle import status.')
  await expect(client.getPuzzleImport('/v1/imports/three')).rejects.toThrow('Unable to read puzzle import status.')
  await expect(client.getPuzzleImport('/v1/imports/four')).rejects.toThrow('Unable to read puzzle import status.')
})

test('rejects failed storage uploads and failed imports', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response(null, { status: 403 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'FAILED', error: 'Bad grid' }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'FAILED', error: null }), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await expect(client.uploadPuzzleFile({ url: 'https://bucket.test', fields: {} }, new File(['x'], 'p.png')))
    .rejects.toThrow('S3 rejected the upload with status 403.')
  await expect(client.waitForPuzzleImport('/v1/imports/one')).rejects.toThrow('Bad grid')
  await expect(client.waitForPuzzleImport('/v1/imports/two')).rejects.toThrow('Puzzle import failed.')
})

test('stops polling when the import attempt limit is reached', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ status: 'PENDING' }), { status: 200 }),
  )
  vi.stubGlobal('fetch', fetchMock)
  vi.stubGlobal('setTimeout', (callback: TimerHandler) => {
    if (typeof callback === 'function') callback()
    return 1
  })
  const client = new ApiClient('https://api.test')

  await expect(client.waitForPuzzleImport('/v1/imports/one', undefined, 179)).rejects.toThrow(
    'Puzzle import is taking longer than expected. Check the puzzle library again shortly.',
  )
  expect(fetchMock).toHaveBeenCalledOnce()
})

test('uses the response message when deleting a puzzle fails', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ message: 'Puzzle is in use' }), { status: 409 }),
  )
  vi.stubGlobal('fetch', fetchMock)
  const client = new ApiClient('https://api.test')

  await expect(client.deletePuzzle('puzzle-1')).rejects.toThrow('Puzzle is in use')
})