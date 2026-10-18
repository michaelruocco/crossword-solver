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