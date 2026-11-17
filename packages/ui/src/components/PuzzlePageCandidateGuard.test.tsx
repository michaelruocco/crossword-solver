import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import type { Puzzle, PuzzleCandidateAnswer, PuzzleClue } from '../apiClient'
import { PuzzlePage } from './PuzzlePage'

const testData = vi.hoisted(() => {
  const clue = { id: 1, direction: 'ACROSS' as const, text: 'A clue', lengths: [3] }
  const candidate = { id: '1A', value: 'CAT', confidenceScore: 90 }
  return {
    clue,
    candidate,
    puzzle: {
      id: 'puzzle-1',
      name: 'Test puzzle',
      createdAt: '2026-10-18T09:30:00Z',
      grid: { numberOfRows: 1, numberOfColumns: 3, cells: [] },
      clues: [clue],
      words: [],
    },
  }
})

const clue = testData.clue satisfies PuzzleClue
const candidate = testData.candidate satisfies PuzzleCandidateAnswer
const puzzle = testData.puzzle satisfies Puzzle

vi.mock('../apiClient', () => ({
  apiClient: {
    getPuzzle: vi.fn().mockResolvedValue(testData.puzzle),
    getAttemptSummaries: vi.fn().mockResolvedValue([]),
    getAttempt: vi.fn(),
    createAttempt: vi.fn(),
    postCandidateAnswers: vi.fn(),
    postAttemptAnswer: vi.fn(),
    deleteAttemptAnswer: vi.fn(),
  },
}))

vi.mock('./PuzzleReadyPage', () => ({
  PuzzleReadyPage: (props: {
    onSelectClue: (selectedClue: PuzzleClue) => void
    onSelectCandidate: (answer: PuzzleCandidateAnswer) => void
  }) => (
    <>
      <button type="button" onClick={() => props.onSelectClue(clue)}>Select clue</button>
      <button type="button" onClick={() => props.onSelectCandidate(candidate)}>Select candidate</button>
    </>
  ),
}))

test('does not submit a selected candidate before its attempt has loaded', async () => {
  render(<PuzzlePage puzzleId={puzzle.id} />)

  fireEvent.click(await screen.findByRole('button', { name: 'Select clue' }))
  fireEvent.click(screen.getByRole('button', { name: 'Select candidate' }))

  const { apiClient } = await import('../apiClient')
  expect(apiClient.postAttemptAnswer).not.toHaveBeenCalled()
})
