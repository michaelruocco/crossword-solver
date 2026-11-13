import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import { apiClient, type Puzzle, type PuzzleAttempt, type PuzzleAttemptSummary } from '../apiClient'
import { PuzzlePage } from './PuzzlePage'

vi.mock('../apiClient', () => ({
  apiClient: { getPuzzle: vi.fn(), getAttemptSummaries: vi.fn(), getAttempt: vi.fn(), createAttempt: vi.fn(), postAttemptAnswer: vi.fn() },
}))

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

const attempt: PuzzleAttempt = {
  id: 'attempt-1',
  createdAt: '2026-10-18T09:30:00Z',
  solving: true,
  puzzle,
  answerCount: 0,
  answers: [],
}

const attemptSummary: PuzzleAttemptSummary = {
  id: 'attempt-1',
  createdAt: '2026-10-18T09:30:00Z',
  solving: true,
  answerCount: 2,
  clueCount: 3,
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(apiClient.getPuzzle).mockResolvedValue(puzzle)
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValue([])
  vi.mocked(apiClient.getAttempt).mockResolvedValue(attempt)
  vi.mocked(apiClient.createAttempt).mockResolvedValue(attempt)
})

function getAnswerInput(index = 1): HTMLInputElement {
  return screen.getByRole('textbox', { name: `Answer character ${index}` }) as HTMLInputElement
}

function enterAnswer(value: string) {
  for (const [index, character] of Array.from(value).entries()) {
    fireEvent.change(getAnswerInput(index + 1), { target: { value: character } })
  }
}

function answerInputValues(length: number): string[] {
  return Array.from({ length }, (_, index) => getAnswerInput(index + 1).value)
}

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

test('loads and selects previous attempts with their summary status', async () => {
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  const previousAttempt = await screen.findByRole('button', { name: /Attempt 1/ })
  expect(previousAttempt.textContent).toContain('2 of 3 answered')
  fireEvent.click(previousAttempt)

  const selectedStatus = screen.getByRole('status', { name: 'Selected attempt status' })
  expect(within(selectedStatus).getByText('2 of 3 clues answered')).toBeTruthy()
  expect(within(selectedStatus).getByText('Solving')).toBeTruthy()
  expect(await within(selectedStatus).findByText('0 saved answers loaded.')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  expect((await screen.findByRole('button', { name: /Attempt 1/ })).getAttribute('aria-pressed')).toBe('true')
})

test('does not reload an attempt when it is already selected', async () => {
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  const previousAttempt = await screen.findByRole('button', { name: /Attempt 1/ })
  fireEvent.click(previousAttempt)
  await screen.findByText('0 saved answers loaded.')
  expect(apiClient.getAttempt).toHaveBeenCalledTimes(1)

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(screen.getByRole('button', { name: /Attempt 1/ }))

  expect(apiClient.getAttempt).toHaveBeenCalledTimes(1)
  expect(screen.getByRole('status', { name: 'Selected attempt status' }).textContent).toContain('0 saved answers loaded.')
})

test('shows a loading state while attempt summaries are being fetched', async () => {
  let resolveSummaries: (summaries: PuzzleAttemptSummary[]) => void = () => undefined
  vi.mocked(apiClient.getAttemptSummaries).mockImplementationOnce(() => new Promise((resolve) => {
    resolveSummaries = resolve
  }))
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  expect(screen.getByText('Loading attempts...')).toBeTruthy()

  await act(async () => {
    resolveSummaries([attemptSummary])
    await Promise.resolve()
  })
  expect(await screen.findByRole('button', { name: /Attempt 1/ })).toBeTruthy()
})

test('ignores a failed attempt-summary request after unmount', async () => {
  let rejectSummaries: (error: Error) => void = () => undefined
  vi.mocked(apiClient.getAttemptSummaries).mockImplementationOnce(() => new Promise((_resolve, reject) => {
    rejectSummaries = reject
  }))
  const { unmount } = render(<PuzzlePage puzzleId={puzzle.id} />)
  const signal = vi.mocked(apiClient.getAttemptSummaries).mock.calls[0][1]
  unmount()
  expect(signal?.aborted).toBe(true)

  await act(async () => {
    rejectSummaries(new Error('Aborted'))
    await Promise.resolve()
  })
})

test('uses a fallback when attempt summaries fail without an Error', async () => {
  vi.mocked(apiClient.getAttemptSummaries).mockRejectedValueOnce('offline')
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Unable to load attempt summaries.')
})

test('shows when there are no previous attempts and leaves unrelated actions unavailable', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  for (const name of ['Auto-solve']) {
    expect((screen.getByRole('button', { name }) as HTMLButtonElement).disabled).toBe(true)
  }
  expect((screen.getByRole('button', { name: 'New attempt' }) as HTMLButtonElement).disabled).toBe(false)
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  expect(await screen.findByText('No attempts yet.')).toBeTruthy()
  expect(screen.getByRole('link', { name: 'Puzzle library' }).getAttribute('href')).toBe('/')
})

test('creates an attempt for the current puzzle and reports success', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect(apiClient.createAttempt).toHaveBeenCalledWith(puzzle.id)
  const selectedStatus = await screen.findByRole('status', { name: 'Selected attempt status' })
  expect(within(selectedStatus).getByText('0 of 3 clues answered')).toBeTruthy()
  expect(await within(selectedStatus).findByText('0 saved answers loaded.')).toBeTruthy()
})

test('creates a new attempt while preserving drafts scoped to an existing attempt', async () => {
  vi.mocked(apiClient.createAttempt)
    .mockResolvedValueOnce(attempt)
    .mockResolvedValueOnce({ ...attempt, id: 'attempt-2' })
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('arc')
  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))
  await screen.findAllByText('0 saved answers loaded.')

  expect(answerInputValues(3)).toEqual(['', '', ''])
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  expect(answerInputValues(3)).toEqual(['', '', ''])
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 2/ }))
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  expect(answerInputValues(3)).toEqual(['A', 'R', 'C'])
})

test('makes a newly created attempt available after attempt history fails to load', async () => {
  vi.mocked(apiClient.getAttemptSummaries).mockRejectedValueOnce(new Error('Attempt history unavailable'))
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  expect((await screen.findByRole('alert')).textContent).toBe('Attempt history unavailable')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))
  await screen.findByRole('status', { name: 'Selected attempt status' })
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))

  expect(await screen.findByRole('button', { name: /Attempt 1/ })).toBeTruthy()
  expect(screen.queryByRole('alert')).toBeNull()
})

test('reports an attempt creation error and allows retrying', async () => {
  vi.mocked(apiClient.createAttempt).mockRejectedValueOnce(new Error('Attempt could not be created'))
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Attempt could not be created')
  expect((screen.getByRole('button', { name: 'New attempt' }) as HTMLButtonElement).disabled).toBe(false)
})

test('uses a fallback when attempt creation fails without an Error', async () => {
  vi.mocked(apiClient.createAttempt).mockRejectedValueOnce('offline')
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Unable to create puzzle attempt.')
})

test('shows the status for an attempt that is not solving', async () => {
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([{ ...attemptSummary, solving: false }])
  render(<PuzzlePage puzzleId={puzzle.id} />)
  await screen.findByRole('table')

  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))

  const selectedStatus = screen.getByRole('status', { name: 'Selected attempt status' })
  expect(within(selectedStatus).getByText('Not solving')).toBeTruthy()
})

test('shows an attempt loading error and retries loading its saved answers', async () => {
  vi.mocked(apiClient.getAttempt)
    .mockRejectedValueOnce(new Error('Attempt unavailable'))
    .mockResolvedValueOnce({ ...attempt, answers: [{ id: '1A', value: 'CAT' }], answerCount: 1 })
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  const alert = await screen.findByRole('alert')
  expect(alert.textContent).toContain('Attempt unavailable')

  fireEvent.click(within(alert).getByRole('button', { name: 'Retry' }))

  expect(await screen.findByText('1 saved answer loaded.')).toBeTruthy()
  expect(apiClient.getAttempt).toHaveBeenCalledTimes(2)
})

test('uses a fallback when loading an attempt fails without an Error', async () => {
  vi.mocked(apiClient.getAttempt).mockRejectedValueOnce('offline')
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))

  expect(await screen.findByText('Unable to load puzzle attempt.')).toBeTruthy()
})

test.each(['resolve', 'reject'] as const)('ignores a late attempt %s after selecting a different attempt', async (outcome) => {
  const otherAttemptSummary = { ...attemptSummary, id: 'attempt-2' }
  let resolveRequest: (value: typeof attempt) => void = () => undefined
  let rejectRequest: (reason: Error) => void = () => undefined
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary, otherAttemptSummary])
  vi.mocked(apiClient.getAttempt)
    .mockImplementationOnce(() => new Promise((resolve, reject) => {
      resolveRequest = resolve
      rejectRequest = reject
    }))
    .mockResolvedValueOnce({
      ...attempt,
      id: otherAttemptSummary.id,
      answerCount: 1,
      answers: [{ id: '1A', value: 'CAT' }],
    })
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  const signal = vi.mocked(apiClient.getAttempt).mock.calls[0][2]
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 2/ }))
  expect(signal?.aborted).toBe(true)
  expect(await screen.findByText('1 saved answer loaded.')).toBeTruthy()

  await act(async () => {
    if (outcome === 'resolve') resolveRequest(attempt)
    else rejectRequest(new Error('Aborted'))
    await Promise.resolve()
  })

  expect(screen.getByRole('status', { name: 'Selected attempt status' }).textContent).toContain('1 saved answer loaded.')
})

test('allows typing and clearing a local answer draft and updates the grid as each character is entered', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  expect(screen.queryByRole('group', { name: 'Answer' })).toBeNull()
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))
  const input = getAnswerInput()
  const clear = screen.getByRole('button', { name: 'Clear answer draft' }) as HTMLButtonElement

  expect(input.value).toBe('')
  expect(clear.disabled).toBe(true)
  expect(screen.getAllByRole('textbox', { name: /^Answer character/ })).toHaveLength(3)
  expect(input.maxLength).toBe(1)
  fireEvent.change(input, { target: { value: 'c' } })
  expect(input.value).toBe('C')
  expect(screen.getByText('Unsaved draft')).toBeTruthy()
  expect(clear.disabled).toBe(false)
  expect((screen.getByRole('button', { name: 'Submit answer' }) as HTMLButtonElement).disabled).toBe(true)
  expect((screen.getByRole('button', { name: 'Delete saved answer' }) as HTMLButtonElement).disabled).toBe(true)
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })
  expect(apiClient.getPuzzle).toHaveBeenCalledOnce()
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, C' })).toBeTruthy()

  fireEvent.click(clear)
  expect(input.value).toBe('')
  expect(answerInputValues(3)).toEqual(['', '', ''])
  expect(clear.disabled).toBe(true)
  expect(screen.getByText('Not submitted', { selector: 'span' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, A' })).toBeTruthy()
})

test('locks crossing letters and displays draft letters in the grid', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  expect(answerInputValues(3)).toEqual(['C', 'A', 'T'])
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, C' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 1, column 2: A' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 1, column 3: T' })).toBeTruthy()

  fireEvent.click(screen.getByRole('button', { name: '1 Down: A vertical entry' }))
  const crossingInput = getAnswerInput(1)
  expect(crossingInput.value).toBe('C')
  expect(crossingInput.disabled).toBe(true)
  expect(getAnswerInput(2).disabled).toBe(false)
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, C' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 2, column 1: 3, empty' })).toBeTruthy()
  fireEvent.change(crossingInput, { target: { value: 'x' } })
  expect(crossingInput.value).toBe('C')
})

test('focuses the first empty editable character when selecting a clue', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: '1 Down: A vertical entry' }))
  fireEvent.change(getAnswerInput(1), { target: { value: 'c' } })
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))

  expect(getAnswerInput(1).disabled).toBe(true)
  expect(document.activeElement).toBe(getAnswerInput(2))
})

test('moves focus to the next editable character input, skipping crossing letters', async () => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({
    ...puzzle,
    clues: [...puzzle.clues, { id: 5, direction: 'DOWN', text: 'Another crossing', lengths: [2] }],
    words: [...puzzle.words, { id: 5, direction: 'DOWN', length: 2, coordinates: { x: 1, y: 1 } }],
  })
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: '5 Down: Another crossing' }))
  fireEvent.change(getAnswerInput(1), { target: { value: 'x' } })
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  expect(getAnswerInput(2).disabled).toBe(true)

  fireEvent.change(getAnswerInput(1), { target: { value: 'c' } })

  expect(document.activeElement).toBe(getAnswerInput(3))
})

test('moves focus to the previous editable input when deleting from an empty character cell', async () => {
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({
    ...puzzle,
    clues: [...puzzle.clues, { id: 5, direction: 'DOWN', text: 'Another crossing', lengths: [2] }],
    words: [...puzzle.words, { id: 5, direction: 'DOWN', length: 2, coordinates: { x: 1, y: 1 } }],
  })
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: '5 Down: Another crossing' }))
  fireEvent.change(getAnswerInput(1), { target: { value: 'x' } })
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  expect(getAnswerInput(2).disabled).toBe(true)

  fireEvent.keyDown(getAnswerInput(3), { key: 'Backspace', code: 'Backspace' })

  expect(document.activeElement).toBe(getAnswerInput(1))

  fireEvent.keyDown(getAnswerInput(3), { key: 'Delete', code: 'Delete' })
  expect(document.activeElement).toBe(getAnswerInput(1))
})

test('preserves independent drafts for across and down clues and only clears the selected draft', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  const across = await screen.findByRole('button', { name: '1 Across: A horizontal entry' })
  const down = screen.getByRole('button', { name: '1 Down: A vertical entry' })

  fireEvent.click(across)
  enterAnswer('arc')
  fireEvent.click(down)
  expect(answerInputValues(2)).toEqual(['A', ''])
  fireEvent.change(getAnswerInput(2), { target: { value: 't' } })

  fireEvent.click(across)
  expect(answerInputValues(3)).toEqual(['A', 'R', 'C'])
  fireEvent.click(screen.getByRole('button', { name: 'Clear answer draft' }))
  fireEvent.click(down)
  expect(answerInputValues(2)).toEqual(['', 'T'])
})

test('submits an answer for the selected attempt and displays it in the clue and grid', async () => {
  const updatedAttempt = { ...attempt, answerCount: 1, answers: [{ id: '1A', value: 'CAT' }] }
  vi.mocked(apiClient.postAttemptAnswer).mockResolvedValueOnce(updatedAttempt)
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }))

  expect(await within(screen.getByRole('region', { name: 'Selected clue' })).findByText(/Saved answer:/)).toBeTruthy()
  expect(screen.getByText('CAT', { selector: 'strong' })).toBeTruthy()
  expect(apiClient.postAttemptAnswer).toHaveBeenCalledWith(puzzle.id, attempt.id, { id: '1A', value: 'CAT' })
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, C' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 1, column 3: T' })).toBeTruthy()
})

test('disables submission without an attempt, without an answer, and while a save is in flight', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  const submitButton = screen.getByRole('button', { name: 'Submit answer' })
  expect((submitButton as HTMLButtonElement).disabled).toBe(true)
  submitButton.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  expect(apiClient.postAttemptAnswer).not.toHaveBeenCalled()

  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  fireEvent.click(screen.getByRole('button', { name: 'Clear answer draft' }))
  expect((submitButton as HTMLButtonElement).disabled).toBe(true)
  submitButton.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  expect(apiClient.postAttemptAnswer).not.toHaveBeenCalled()

  let resolveSave: (value: typeof attempt) => void = () => undefined
  vi.mocked(apiClient.postAttemptAnswer).mockImplementationOnce(() => new Promise((resolve) => {
    resolveSave = resolve
  }))
  enterAnswer('cat')
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }))
  const submittingButton = screen.getByRole('button', { name: 'Submitting answer' })
  expect((submittingButton as HTMLButtonElement).disabled).toBe(true)
  expect(apiClient.postAttemptAnswer).toHaveBeenCalledTimes(1)

  await act(async () => {
    resolveSave({ ...attempt, answerCount: 1, answers: [{ id: '1A', value: 'CAT' }] })
    await Promise.resolve()
  })
  expect(await screen.findByText('1 saved answer loaded.')).toBeTruthy()
})

test('removes only the submitted draft and ignores a response for a different attempt', async () => {
  const mismatchedAttempt = {
    ...attempt,
    id: 'another-attempt',
    answerCount: 1,
    answers: [{ id: '1A', value: 'CAT' }],
  }
  vi.mocked(apiClient.postAttemptAnswer).mockResolvedValueOnce(mismatchedAttempt)
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  fireEvent.click(screen.getByRole('button', { name: '1 Down: A vertical entry' }))
  fireEvent.change(getAnswerInput(2), { target: { value: 't' } })
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }))

  expect(await screen.findByText('Not submitted', { selector: 'span' })).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: '1 Down: A vertical entry' }))
  expect(answerInputValues(2)).toEqual(['', 'T'])
  expect(screen.getByText('0 saved answers loaded.')).toBeTruthy()
  expect(screen.queryByText('1 saved answer loaded.')).toBeNull()
  expect(screen.queryByText('Saved answer:', { selector: 'p' })).toBeNull()
})

test('keeps unsaved clue drafts when a new attempt is created', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('arc')
  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')

  expect(answerInputValues(3)).toEqual(['A', 'R', 'C'])
})

test('shows saved answers when a previous attempt is selected', async () => {
  const savedAttempt = { ...attempt, answerCount: 1, answers: [{ id: '1A', value: 'CAT' }] }
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  vi.mocked(apiClient.getAttempt).mockResolvedValueOnce(savedAttempt)
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  await screen.findByText('1 saved answer loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))

  expect(within(screen.getByRole('region', { name: 'Selected clue' })).getByText(/Saved answer:/)).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, C' })).toBeTruthy()

  fireEvent.click(screen.getByRole('button', { name: '1 Down: A vertical entry' }))
  expect(getAnswerInput(1).value).toBe('C')
  expect(getAnswerInput(1).disabled).toBe(true)
  expect(getAnswerInput(2).disabled).toBe(false)
})

test('keeps the answer draft and shows a useful error when submission fails', async () => {
  vi.mocked(apiClient.postAttemptAnswer).mockRejectedValueOnce(new Error('Clue not found'))
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }))

  expect((await screen.findByRole('alert')).textContent).toContain('Clue not found')
  expect(answerInputValues(3)).toEqual(['C', 'A', 'T'])
})

test('uses a fallback when answer submission fails without an Error', async () => {
  vi.mocked(apiClient.postAttemptAnswer).mockRejectedValueOnce('offline')
  render(<PuzzlePage puzzleId={puzzle.id} />)
  fireEvent.click(await screen.findByRole('button', { name: 'New attempt' }))
  await screen.findByText('0 saved answers loaded.')
  fireEvent.click(screen.getByRole('button', { name: '1 Across: A horizontal entry' }))
  enterAnswer('cat')
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }))

  expect((await screen.findByRole('alert')).textContent).toContain('Unable to save attempt answer.')
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

test('renders saved down answers in the grid and limits them to the word length', async () => {
  const savedAttempt = { ...attempt, answerCount: 1, answers: [{ id: '1D', value: 'b t x' }] }
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  vi.mocked(apiClient.getAttempt).mockResolvedValueOnce(savedAttempt)
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  await screen.findByText('1 saved answer loaded.')

  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, B' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 2, column 1: 3, T' })).toBeTruthy()
})

test('ignores saved answers without matching clues or word positions', async () => {
  const savedAttempt = { ...attempt, answers: [{ id: '99A', value: 'ABC' }, { id: '3A', value: 'XY' }] }
  vi.mocked(apiClient.getPuzzle).mockResolvedValueOnce({ ...puzzle, words: puzzle.words.filter((word) => word.id !== 3) })
  vi.mocked(apiClient.getAttemptSummaries).mockResolvedValueOnce([attemptSummary])
  vi.mocked(apiClient.getAttempt).mockResolvedValueOnce(savedAttempt)
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(await screen.findByRole('button', { name: /Attempt 1/ }))
  await screen.findByText('2 saved answers loaded.')

  expect(screen.getByRole('cell', { name: 'Row 2, column 1: 3, empty' })).toBeTruthy()
  expect(screen.queryByText('ABC')).toBeNull()
})