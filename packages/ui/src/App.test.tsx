import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'

const { apiClientMock } = vi.hoisted(() => ({
  apiClientMock: {
    getAllPuzzleSummaries: vi.fn(),
    getPuzzle: vi.fn(),
    deletePuzzle: vi.fn(),
    startPuzzleImport: vi.fn(),
    waitForPuzzleImport: vi.fn(),
    getPuzzleGridImageUrl: vi.fn((puzzleId: string) => `/v1/puzzles/${puzzleId}/grid-images`),
  },
}))

vi.mock('./apiClient', () => ({ apiClient: apiClientMock }))

import App from './App'

const puzzle = {
  id: 'puzzle-1',
  name: 'Sunday Cryptic',
  createdAt: '2026-10-18T09:30:00Z',
  clueCount: 27,
}

beforeEach(() => {
  window.history.replaceState(null, '', '/')
  vi.clearAllMocks()
  apiClientMock.getAllPuzzleSummaries.mockResolvedValue([puzzle])
  apiClientMock.deletePuzzle.mockResolvedValue(undefined)
  apiClientMock.startPuzzleImport.mockResolvedValue({ location: '/v1/puzzles/imports/import-1' })
  apiClientMock.waitForPuzzleImport.mockResolvedValue({ status: 'COMPLETE', puzzleId: puzzle.id })
  apiClientMock.getPuzzle.mockResolvedValue({ ...puzzle, grid: { numberOfRows: 1, numberOfColumns: 1, cells: [] }, clues: [], words: [] })
})

test('opens a linked puzzle and returns to the library on hash navigation', async () => {
  render(<App />)
  const link = await screen.findByRole('link', { name: 'View puzzle Sunday Cryptic' })

  act(() => {
    window.history.pushState(null, '', link.getAttribute('href'))
    window.dispatchEvent(new HashChangeEvent('hashchange'))
  })
  expect(await screen.findByRole('table', { name: 'Puzzle grid' })).toBeTruthy()
  expect(screen.queryByRole('heading', { name: 'Puzzle library' })).toBeNull()
  expect(apiClientMock.getPuzzle).toHaveBeenCalledWith(puzzle.id, expect.any(AbortSignal))

  act(() => {
    window.history.pushState(null, '', screen.getByRole('link', { name: 'Puzzle library' }).getAttribute('href'))
    window.dispatchEvent(new HashChangeEvent('hashchange'))
  })
  expect(await screen.findByRole('heading', { name: 'Puzzle library' })).toBeTruthy()
})

test('loads a puzzle directly from its encoded URL', async () => {
  window.history.replaceState(null, '', '/#puzzle=puzzle%20%2F1')
  render(<App />)

  expect(await screen.findByRole('table', { name: 'Puzzle grid' })).toBeTruthy()
  expect(apiClientMock.getPuzzle).toHaveBeenCalledWith('puzzle /1', expect.any(AbortSignal))
})

test('loads the library and shows its connected state', async () => {
  render(<App />)

  expect(await screen.findByRole('heading', { name: 'Sunday Cryptic' })).toBeTruthy()
  expect(screen.getByText('Library synced')).toBeTruthy()
  expect(apiClientMock.getAllPuzzleSummaries).toHaveBeenCalledOnce()
})

test('shows a fallback load error and retries successfully', async () => {
  apiClientMock.getAllPuzzleSummaries.mockRejectedValueOnce('offline').mockResolvedValueOnce([puzzle])
  render(<App />)

  expect(await screen.findByText('Something went wrong while loading puzzles.')).toBeTruthy()
  expect(screen.getByText('Connection issue')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }))

  expect(await screen.findByRole('heading', { name: 'Sunday Cryptic' })).toBeTruthy()
  expect(apiClientMock.getAllPuzzleSummaries).toHaveBeenCalledTimes(2)
})

test('shows the API error message when loading rejects with an Error', async () => {
  apiClientMock.getAllPuzzleSummaries.mockRejectedValueOnce(new Error('API unavailable'))
  render(<App />)

  expect(await screen.findByText('API unavailable')).toBeTruthy()
})

test('ignores a load rejection after the request has been aborted', async () => {
  let rejectLoad: (error: Error) => void = () => undefined
  apiClientMock.getAllPuzzleSummaries.mockImplementationOnce(
    () => new Promise((_resolve, reject) => { rejectLoad = reject }),
  )
  const { unmount } = render(<App />)
  const signal = apiClientMock.getAllPuzzleSummaries.mock.calls[0][0] as AbortSignal

  unmount()
  expect(signal.aborted).toBe(true)

  await act(async () => {
    rejectLoad(new Error('Request aborted'))
    await Promise.resolve()
  })
})

test('opens and closes the upload dialog', async () => {
  render(<App />)
  await screen.findByRole('heading', { name: 'Sunday Cryptic' })

  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))
  const dialog = screen.getByRole('dialog', { name: 'Upload a puzzle' })
  fireEvent.click(within(dialog).getByRole('button', { name: 'Close upload dialog' }))

  expect(screen.queryByRole('dialog', { name: 'Upload a puzzle' })).toBeNull()
})

test('opens the separate URL import dialog and refreshes the library after completion', async () => {
  render(<App />)
  await screen.findByRole('heading', { name: 'Sunday Cryptic' })

  fireEvent.click(screen.getByRole('button', { name: 'Import from URL' }))
  expect(screen.queryByRole('dialog', { name: 'Upload a puzzle' })).toBeNull()
  fireEvent.change(screen.getByRole('textbox', { name: 'Image URL' }), {
    target: { value: 'https://images.test/puzzle.png' },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Import puzzle' }))

  expect(await screen.findByRole('heading', { name: 'Puzzle imported' })).toBeTruthy()
  await waitFor(() => expect(apiClientMock.getAllPuzzleSummaries).toHaveBeenCalledTimes(2))
  expect(apiClientMock.startPuzzleImport).toHaveBeenCalledWith('https://images.test/puzzle.png', expect.any(AbortSignal))
  expect(apiClientMock.waitForPuzzleImport).toHaveBeenCalledWith('/v1/puzzles/imports/import-1', expect.any(AbortSignal))
  fireEvent.click(screen.getByRole('button', { name: 'Done' }))
  expect(screen.queryByRole('dialog', { name: 'Import from URL' })).toBeNull()
})

test('deletes a puzzle from the library after confirmation', async () => {
  render(<App />)
  await screen.findByRole('heading', { name: 'Sunday Cryptic' })

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  fireEvent.click(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }))

  expect(await screen.findByText('Your library is empty')).toBeTruthy()
  expect(apiClientMock.deletePuzzle).toHaveBeenCalledWith('puzzle-1')
})