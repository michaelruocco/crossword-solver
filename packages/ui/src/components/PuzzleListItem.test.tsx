import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { PuzzleListItem } from './PuzzleListItem'

const puzzle = {
  id: 'puzzle-id-1',
  name: 'Sunday Cryptic',
  createdAt: '2026-10-18T09:30:00Z',
  clueCount: 27,
}

test('shows the puzzle summary and grid image link', () => {
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={vi.fn().mockResolvedValue(undefined)} />)
  const gridPath = '/v1/puzzles/puzzle-id-1/grid-images'
  const expectedGridUrl = import.meta.env.VITE_API_BASE_URL
    ? new URL(gridPath, import.meta.env.VITE_API_BASE_URL).toString()
    : gridPath

  expect(screen.getByRole('heading', { name: 'Sunday Cryptic' })).toBeTruthy()
  expect(screen.getByText('puzzle-id-1')).toBeTruthy()
  expect(screen.getByText('27', { exact: true })).toBeTruthy()
  expect(screen.getByRole('img', { name: 'Grid preview for Sunday Cryptic' }).getAttribute('src')).toBe(expectedGridUrl)
  expect(screen.getByRole('link', { name: 'Open grid image for Sunday Cryptic' }).getAttribute('href')).toBe(expectedGridUrl)
})

test('shows a fallback when the grid preview fails to load', () => {
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={vi.fn().mockResolvedValue(undefined)} />)

  fireEvent.error(screen.getByRole('img', { name: 'Grid preview for Sunday Cryptic' }))

  expect(screen.getByLabelText('Grid preview unavailable')).toBeTruthy()
})

test('requires confirmation before deleting a puzzle', () => {
  const onDelete = vi.fn().mockResolvedValue(undefined)
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={onDelete} />)

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  expect(onDelete).not.toHaveBeenCalled()

  fireEvent.click(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }))
  expect(onDelete).toHaveBeenCalledWith(puzzle.id)
})