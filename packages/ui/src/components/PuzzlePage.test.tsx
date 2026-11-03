import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import { apiClient, type Puzzle } from '../apiClient'
import { PuzzlePage } from './PuzzlePage'

vi.mock('../apiClient', () => ({ apiClient: { getPuzzle: vi.fn(), createAttempt: vi.fn() } }))

const puzzle: Puzzle = {
  id: 'puzzle-1',
  name: 'Sunday Cryptic',
  createdAt: '2026-10-18T09:30:00Z',
  grid: {
    numberOfRows: 2,
    numberOfColumns: 3,
    cells: [
      { id: null, coordinates: { x: 2, y: 0 }, black: true, character: null },
      { id: 1, coordinates: { x: 0, y: 1 }, black: false, character: 'A' },
      { id: null, coordinates: { x: 1, y: 1 }, black: false, character: null },
      { id: null, coordinates: { x: 2, y: 1 }, black: false, character: null },
      { id: 3, coordinates: { x: 0, y: 0 }, black: false, character: null },
      { id: null, coordinates: { x: 1, y: 0 }, black: false, character: null },
    ],
  },
  clues: [
    { id: 3, direction: 'ACROSS', text: 'A second entry', lengths: [1, 1] },
    { id: 1, direction: 'DOWN', text: 'A vertical entry', lengths: [2] },
    { id: 1, direction: 'ACROSS', text: 'A horizontal entry', lengths: [3] },
  ],
  words: [
    { id: 1, direction: 'ACROSS', length: 3, coordinates: { x: 0, y: 1 } },
    { id: 1, direction: 'DOWN', length: 2, coordinates: { x: 0, y: 1 } },
    { id: 3, direction: 'ACROSS', length: 2, coordinates: { x: 0, y: 0 } },
  ],
}

const attempt = {
  id: 'attempt-1',
  createdAt: '2026-10-18T09:30:00Z',
  solving: true,
  puzzle,
  answerCount: 0,
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(apiClient.getPuzzle).mockResolvedValue(puzzle)
  vi.mocked(apiClient.createAttempt).mockResolvedValue(attempt)
})

test('maps bottom-left-origin coordinates to top-to-bottom display rows without reversing columns', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)

  expect(screen.getByRole('status').textContent).toBe('Loading puzzle...')
  expect(await screen.findByRole('heading', { name: puzzle.name })).toBeTruthy()
  const grid = screen.getByRole('table', { name: 'Puzzle grid' })
  const cells = within(grid).getAllByRole('cell')
  expect(cells).toHaveLength(6)
  expect(cells[0].getAttribute('aria-label')).toBe('Row 1, column 1: 1, A')
  expect(cells[1].getAttribute('aria-label')).toBe('Row 1, column 2: empty')
  expect(cells[3].getAttribute('aria-label')).toBe('Row 2, column 1: 3, empty')
  expect(cells[5].getAttribute('aria-label')).toBe('Row 2, column 3: black square')
  expect(within(grid).getByText('A')).toBeTruthy()
  expect(screen.queryByRole('img')).toBeNull()
  expect(apiClient.getPuzzle).toHaveBeenCalledWith(puzzle.id, expect.any(AbortSignal))
})

test('groups and sorts clues', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  const across = screen.getByRole('region', { name: 'Across' })
  const clues = within(across).getAllByRole('button')
  expect(clues[0].textContent).toBe('1A horizontal entry')
  expect(clues[1].textContent).toBe('3A second entry')
  expect(within(screen.getByRole('region', { name: 'Down' })).getByText('A vertical entry')).toBeTruthy()
})

test.each([
  { lengths: [], text: 'A horizontal entry' },
  { lengths: [3], text: 'A horizontal entry' },
  { lengths: [1, 2], text: 'A horizontal entry' },
  { lengths: [1, 2], text: 'A horizontal entry (1, 2)' },
])('renders only the clue text "$text" with lengths $lengths', async ({ lengths, text }) => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({
    ...puzzle,
    clues: [{ id: 1, direction: 'ACROSS', text, lengths }],
  })
  render(<PuzzlePage puzzleId={puzzle.id} />)

  const clue = await screen.findByRole('button', { name: `1 Across: ${text}` })
  expect(clue.textContent).toBe(`1${text}`)

  fireEvent.click(clue)
  const selected = screen.getByRole('region', { name: 'Selected clue' })
  expect(selected.querySelector('p')?.textContent).toBe(text)
})

test('selects across and down entries independently when their numbers match', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  const across = await screen.findByRole('button', { name: '1 Across: A horizontal entry' })
  const down = screen.getByRole('button', { name: '1 Down: A vertical entry' })
  const cells = within(screen.getByRole('table')).getAllByRole('cell')

  fireEvent.click(across)
  expect(across.getAttribute('aria-pressed')).toBe('true')
  expect(down.getAttribute('aria-pressed')).toBe('false')
  expect(cells.filter((cell) => cell.classList.contains('puzzle-cell-selected'))).toHaveLength(3)
  expect(cells.slice(0, 3).every((cell) => cell.classList.contains('puzzle-cell-selected'))).toBe(true)
  expect(screen.getByRole('region', { name: 'Selected clue' }).textContent).toContain('1 Across')
  expect((screen.getByRole('button', { name: 'Submit answer' }) as HTMLButtonElement).disabled).toBe(true)

  fireEvent.click(down)
  expect(across.getAttribute('aria-pressed')).toBe('false')
  expect(down.getAttribute('aria-pressed')).toBe('true')
  expect(cells.filter((cell) => cell.classList.contains('puzzle-cell-selected'))).toHaveLength(2)
  expect(cells[3].classList.contains('puzzle-cell-selected')).toBe(true)
  expect(cells[1].classList.contains('puzzle-cell-selected')).toBe(false)
  expect(screen.getByRole('region', { name: 'Selected clue' }).textContent).toContain('1 Down')
})

test('highlights a down entry toward decreasing y without extending above or below the word', async () => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({
    ...puzzle,
    grid: {
      numberOfRows: 4,
      numberOfColumns: 1,
      cells: Array.from({ length: 4 }, (_, y) => ({ id: null, coordinates: { x: 0, y }, black: false, character: null })),
    },
    words: [{ id: 1, direction: 'DOWN', length: 2, coordinates: { x: 0, y: 2 } }],
  })
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: '1 Down: A vertical entry' }))

  const cells = within(screen.getByRole('table')).getAllByRole('cell')
  expect(cells.map((cell) => cell.classList.contains('puzzle-cell-selected'))).toEqual([false, true, true, false])
})

test('keeps attempt history and auto-solve unavailable while enabling new attempts', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  for (const name of ['Previous attempts', 'Auto-solve']) {
    expect((screen.getByRole('button', { name }) as HTMLButtonElement).disabled).toBe(true)
  }
  expect((screen.getByRole('button', { name: 'New attempt' }) as HTMLButtonElement).disabled).toBe(false)
  expect(screen.getByText('No attempt created')).toBeTruthy()
  expect(screen.getByRole('link', { name: 'Puzzle library' }).getAttribute('href')).toBe('/')
})

test('creates an attempt for the current puzzle and reports success', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect(apiClient.createAttempt).toHaveBeenCalledWith(puzzle.id)
  expect(await screen.findByText('Attempt created')).toBeTruthy()
})

test('reports an attempt creation error and allows retrying', async () => {
  vi.mocked(apiClient.createAttempt).mockRejectedValueOnce(new Error('Attempt could not be created'))
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Attempt could not be created')
  expect((screen.getByRole('button', { name: 'New attempt' }) as HTMLButtonElement).disabled).toBe(false)
})

test('allows typing and clearing a local answer draft without submitting or modifying the grid', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  expect(screen.queryByRole('textbox', { name: 'Answer draft' })).toBeNull()
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))
  const input = screen.getByRole('textbox', { name: 'Answer draft' }) as HTMLInputElement
  const clear = screen.getByRole('button', { name: 'Clear answer draft' }) as HTMLButtonElement

  expect(input.value).toBe('')
  expect(clear.disabled).toBe(true)
  fireEvent.change(input, { target: { value: 'arc' } })
  expect(input.value).toBe('arc')
  expect(screen.getByText('Unsaved draft')).toBeTruthy()
  expect(clear.disabled).toBe(false)
  expect((screen.getByRole('button', { name: 'Submit answer' }) as HTMLButtonElement).disabled).toBe(true)
  expect((screen.getByRole('button', { name: 'Delete saved answer' }) as HTMLButtonElement).disabled).toBe(true)
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })
  expect(apiClient.getPuzzle).toHaveBeenCalledOnce()
  expect(screen.getByRole('cell', { name: 'Row 1, column 2: empty' })).toBeTruthy()

  fireEvent.click(clear)
  expect(input.value).toBe('')
  expect(clear.disabled).toBe(true)
  expect(screen.getByText('Not submitted')).toBeTruthy()
})

test('preserves independent drafts for across and down clues and only clears the selected draft', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  const across = await screen.findByRole('button', { name: '1 Across: A horizontal entry' })
  const down = screen.getByRole('button', { name: '1 Down: A vertical entry' })

  fireEvent.click(across)
  fireEvent.change(screen.getByRole('textbox', { name: 'Answer draft' }), { target: { value: 'arc' } })
  fireEvent.click(down)
  expect((screen.getByRole('textbox', { name: 'Answer draft' }) as HTMLInputElement).value).toBe('')
  fireEvent.change(screen.getByRole('textbox', { name: 'Answer draft' }), { target: { value: 'at' } })

  fireEvent.click(across)
  expect((screen.getByRole('textbox', { name: 'Answer draft' }) as HTMLInputElement).value).toBe('arc')
  fireEvent.click(screen.getByRole('button', { name: 'Clear answer draft' }))
  fireEvent.click(down)
  expect((screen.getByRole('textbox', { name: 'Answer draft' }) as HTMLInputElement).value).toBe('at')
})

test('retries a failed request and displays the API error', async () => {
  vi.mocked(apiClient.getPuzzle).mockRejectedValueOnce(new Error('Puzzle not found'))
  render(<PuzzlePage puzzleId={puzzle.id} />)

  expect(await screen.findByRole('alert')).toBeTruthy()
  expect(screen.getByText('Puzzle not found')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }))

  expect(await screen.findByRole('table')).toBeTruthy()
  expect(apiClient.getPuzzle).toHaveBeenCalledTimes(2)
})

test('uses a fallback for non-Error request failures', async () => {
  vi.mocked(apiClient.getPuzzle).mockRejectedValueOnce('offline')
  render(<PuzzlePage puzzleId={puzzle.id} />)
  expect(await screen.findByText('Unable to load puzzle.')).toBeTruthy()
})

test.each(['resolve', 'reject'] as const)('aborts on unmount and ignores a late %s', async (outcome) => {
  let resolveRequest: (value: Puzzle) => void = () => undefined
  let rejectRequest: (reason: Error) => void = () => undefined
  vi.mocked(apiClient.getPuzzle).mockImplementationOnce(() => new Promise((resolve, reject) => {
    resolveRequest = resolve
    rejectRequest = reject
  }))
  const { unmount } = render(<PuzzlePage puzzleId={puzzle.id} />)
  const signal = vi.mocked(apiClient.getPuzzle).mock.calls[0][1]
  unmount()
  expect(signal?.aborted).toBe(true)

  await act(async () => {
    if (outcome === 'resolve') resolveRequest(puzzle)
    else rejectRequest(new Error('Aborted'))
    await Promise.resolve()
  })
})

test('handles missing clues and an unavailable grid', async () => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({ ...puzzle, name: '', clues: [], grid: { numberOfRows: 0, numberOfColumns: 0, cells: [] } })
  render(<PuzzlePage puzzleId={puzzle.id} />)

  expect(await screen.findByRole('heading', { name: 'Untitled puzzle' })).toBeTruthy()
  expect(screen.getByText('Grid unavailable.')).toBeTruthy()
  expect(screen.getByText('No across clues.')).toBeTruthy()
  expect(screen.getByText('No down clues.')).toBeTruthy()
})

test('renders missing cells as black squares and tolerates clues without word positions', async () => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({ ...puzzle, words: [], grid: { ...puzzle.grid, cells: [] } })
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))

  const cells = within(screen.getByRole('table')).getAllByRole('cell')
  expect(cells.every((cell) => cell.classList.contains('puzzle-cell-black'))).toBe(true)
  expect(screen.getByRole('region', { name: 'Selected clue' })).toBeTruthy()
})