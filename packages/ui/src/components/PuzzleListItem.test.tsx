import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import { PuzzleListItem } from './PuzzleListItem'

const puzzle = {
  id: 'puzzle-id-1',
  name: 'Sunday Cryptic',
  createdAt: '2026-10-18T09:30:00Z',
  clueCount: 27,
}

test('shows the puzzle summary and grid image link', () => {
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} />)

  expect(screen.getByRole('heading', { name: 'Sunday Cryptic' })).toBeTruthy()
  expect(screen.getByText('puzzle-id-1')).toBeTruthy()
  expect(screen.getByText('27', { exact: true })).toBeTruthy()
  expect(screen.getByRole('img', { name: 'Grid preview for Sunday Cryptic' }).getAttribute('src')).toBe(
    '/v1/puzzles/puzzle-id-1/grid-images',
  )
  expect(screen.getByRole('link', { name: 'Open grid image for Sunday Cryptic' }).getAttribute('href')).toBe(
    '/v1/puzzles/puzzle-id-1/grid-images',
  )
})

test('shows a fallback when the grid preview fails to load', () => {
  render(<PuzzleListItem puzzle={puzzle} rowIndex={0} />)

  fireEvent.error(screen.getByRole('img', { name: 'Grid preview for Sunday Cryptic' }))

  expect(screen.getByLabelText('Grid preview unavailable')).toBeTruthy()
})