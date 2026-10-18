import { fireEvent, render, screen, within } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { PuzzleListPage } from './PuzzleListPage'

const puzzles = [
  { id: 'one', name: 'Sunday Cryptic', createdAt: '2026-10-17T09:30:00Z', clueCount: 27 },
  { id: 'two', name: 'Quick Grid', createdAt: '2026-10-18T09:30:00Z', clueCount: 15 },
  { id: 'three', name: 'Sunday Special', createdAt: '2026-10-16T09:30:00Z', clueCount: 34 },
]

test('filters puzzles by name', () => {
  render(<PuzzleListPage puzzles={puzzles} loadState="ready" errorMessage="" onRefresh={vi.fn()} />)

  fireEvent.change(screen.getByRole('searchbox', { name: 'Search puzzles' }), { target: { value: 'sunday' } })

  const list = screen.getByLabelText('Puzzle summaries')
  expect(within(list).getByRole('heading', { name: 'Sunday Cryptic' })).toBeTruthy()
  expect(within(list).getByRole('heading', { name: 'Sunday Special' })).toBeTruthy()
  expect(within(list).queryByRole('heading', { name: 'Quick Grid' })).toBeNull()
})

test('sorts puzzles by clue count', () => {
  render(<PuzzleListPage puzzles={puzzles} loadState="ready" errorMessage="" onRefresh={vi.fn()} />)

  fireEvent.change(screen.getByRole('combobox', { name: 'Sort puzzles' }), { target: { value: 'most-clues' } })

  const names = screen.getAllByRole('heading', { level: 2 }).map((heading) => heading.textContent)
  expect(names).toEqual(['Sunday Special', 'Sunday Cryptic', 'Quick Grid'])
})

test('shows an empty-library state when there are no puzzles', () => {
  render(<PuzzleListPage puzzles={[]} loadState="ready" errorMessage="" onRefresh={vi.fn()} />)

  expect(screen.getByRole('heading', { name: 'Your library is empty' })).toBeTruthy()
})