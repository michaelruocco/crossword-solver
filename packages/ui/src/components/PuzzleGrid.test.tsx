import { render, screen, within } from '@testing-library/react'
import { expect, test } from 'vitest'
import type { Puzzle, PuzzleAnswer, PuzzleClue } from '../apiClient'
import { PuzzleGrid } from './PuzzleGrid'

const puzzle: Puzzle = {
  id: 'grid-test',
  name: 'Grid test',
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
    { id: 1, direction: 'ACROSS', text: 'Across', lengths: [3] },
    { id: 1, direction: 'DOWN', text: 'Down', lengths: [2] },
    { id: 3, direction: 'ACROSS', text: 'Second across', lengths: [2] },
  ],
  words: [
    { id: 1, direction: 'ACROSS', length: 3, coordinates: { x: 0, y: 1 } },
    { id: 1, direction: 'DOWN', length: 2, coordinates: { x: 0, y: 1 } },
    { id: 3, direction: 'ACROSS', length: 2, coordinates: { x: 0, y: 0 } },
  ],
}

function renderGrid(options: {
  selectedClue?: PuzzleClue | null
  answers?: PuzzleAnswer[]
  value?: Puzzle
} = {}) {
  return render(
    <PuzzleGrid
      puzzle={options.value ?? puzzle}
      selectedClue={options.selectedClue ?? null}
      answers={options.answers ?? []}
      drafts={[]}
    />,
  )
}

test('maps bottom-left-origin coordinates to displayed rows without reversing columns', () => {
  renderGrid()

  const cells = within(screen.getByRole('table', { name: 'Puzzle grid' })).getAllByRole('cell')
  expect(cells).toHaveLength(6)
  expect(cells[0].getAttribute('aria-label')).toBe('Row 1, column 1: 1, A')
  expect(cells[1].getAttribute('aria-label')).toBe('Row 1, column 2: empty')
  expect(cells[3].getAttribute('aria-label')).toBe('Row 2, column 1: 3, empty')
  expect(cells[5].getAttribute('aria-label')).toBe('Row 2, column 3: black square')
})

test('highlights a down word only across its cells while decreasing y', () => {
  renderGrid({ selectedClue: puzzle.clues[1] })

  const cells = within(screen.getByRole('table')).getAllByRole('cell')
  expect(cells.map((cell) => cell.classList.contains('puzzle-cell-selected'))).toEqual([
    true, false, false,
    true, false, false,
  ])
})

test('shows saved down answers in the grid and limits them to the word length', () => {
  renderGrid({ answers: [{ id: '1D', value: 'b t x' }] })

  expect(screen.getByRole('cell', { name: 'Row 1, column 1: 1, B' })).toBeTruthy()
  expect(screen.getByRole('cell', { name: 'Row 2, column 1: 3, T' })).toBeTruthy()
})

test('renders missing cells as black and ignores saved answers without clue or word positions', () => {
  const noWords = { ...puzzle, words: [], grid: { ...puzzle.grid, cells: [] } }
  const { rerender } = renderGrid({
    value: noWords,
    selectedClue: puzzle.clues[0],
    answers: [{ id: '99A', value: 'ABC' }, { id: '3A', value: 'XY' }],
  })

  expect(within(screen.getByRole('table')).getAllByRole('cell').every((cell) => (
    cell.classList.contains('puzzle-cell-black')
  ))).toBe(true)
  expect(screen.queryByText('ABC')).toBeNull()

  rerender(<PuzzleGrid puzzle={{ ...puzzle, grid: { numberOfRows: 0, numberOfColumns: 0, cells: [] } }} selectedClue={null} answers={[]} drafts={[]} />)
  expect(screen.getByText('Grid unavailable.')).toBeTruthy()
})
