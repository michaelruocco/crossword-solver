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

test('shows a fallback when the puzzle date is invalid', () => {
  render(
    <PuzzleListItem
      puzzle={{ ...puzzle, createdAt: 'not-a-date' }}
      rowIndex={0}
      onDelete={vi.fn().mockResolvedValue(undefined)}
    />,
  )

  expect(screen.getByText('Date unavailable')).toBeTruthy()
})

test('requires confirmation before deleting a puzzle', () => {
  const onDelete = vi.fn().mockResolvedValue(undefined)
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={onDelete} />)

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  expect(onDelete).not.toHaveBeenCalled()

  fireEvent.click(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }))
  expect(onDelete).toHaveBeenCalledWith(puzzle.id)
})

test('allows cancelling a delete confirmation', () => {
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={vi.fn().mockResolvedValue(undefined)} />)

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))

  expect(screen.getByRole('button', { name: 'Delete Sunday Cryptic' })).toBeTruthy()
})

test('shows the delete error returned by the handler and allows retry', async () => {
  const onDelete = vi.fn().mockRejectedValue(new Error('Delete service unavailable'))
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={onDelete} />)

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  fireEvent.click(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Delete service unavailable')
  expect(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }).textContent).toBe('Delete')
})

test('shows a fallback when deletion rejects with a non-Error value', async () => {
  const onDelete = vi.fn().mockRejectedValue('offline')
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} onDelete={onDelete} />)

  fireEvent.click(screen.getByRole('button', { name: 'Delete Sunday Cryptic' }))
  fireEvent.click(screen.getByRole('button', { name: 'Confirm delete Sunday Cryptic' }))

  expect((await screen.findByRole('alert')).textContent).toBe('Unable to delete this puzzle.')
})