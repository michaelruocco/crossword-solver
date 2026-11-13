import { fireEvent, render, screen, within } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import type { PuzzleClue } from '../apiClient'
import { PuzzleClueList } from './PuzzleClueList'

const clues: PuzzleClue[] = [
  { id: 3, direction: 'ACROSS', text: 'Third across', lengths: [1, 2] },
  { id: 1, direction: 'DOWN', text: 'First down', lengths: [2] },
  { id: 1, direction: 'ACROSS', text: 'First across', lengths: [] },
]

test('groups and sorts clues by direction and number', () => {
  render(<PuzzleClueList clues={clues} savedAnswers={[]} selectedClue={null} onSelect={vi.fn()} />)

  const across = within(screen.getByRole('region', { name: 'Across' })).getAllByRole('button')
  expect(across.map((clue) => clue.textContent)).toEqual(['1First across', '3Third across'])
  expect(within(screen.getByRole('region', { name: 'Down' })).getByText('First down')).toBeTruthy()
})

test('shows clue text without length metadata and calls the selection handler', () => {
  const onSelect = vi.fn()
  render(<PuzzleClueList clues={clues} savedAnswers={[]} selectedClue={null} onSelect={onSelect} />)

  const clue = screen.getByRole('button', { name: '3 Across: Third across' })
  expect(clue.textContent).toBe('3Third across')
  fireEvent.click(clue)

  expect(onSelect).toHaveBeenCalledWith(clues[0])
})

test('marks the selected clue, displays its saved answer, and handles empty directions', () => {
  const selectedClue = clues[0]
  render(
    <PuzzleClueList
      clues={[selectedClue]}
      savedAnswers={[{ id: '3A', value: 'CAT' }]}
      selectedClue={selectedClue}
      onSelect={vi.fn()}
    />,
  )

  expect(screen.getByRole('button', { name: '3 Across: Third across' }).getAttribute('aria-pressed')).toBe('true')
  expect(screen.getByText('CAT')).toBeTruthy()
  expect(screen.getByText('No down clues.')).toBeTruthy()
})
