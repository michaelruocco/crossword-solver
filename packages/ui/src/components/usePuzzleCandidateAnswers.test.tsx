import { act, renderHook } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import { apiClient, type PuzzleClue } from '../apiClient'
import { usePuzzleCandidateAnswers } from './usePuzzleCandidateAnswers'

vi.mock('../apiClient', () => ({
  apiClient: {
    postCandidateAnswers: vi.fn(),
  },
}))

const clue: PuzzleClue = { id: 1, direction: 'ACROSS', text: 'A clue', lengths: [3] }

beforeEach(() => {
  vi.resetAllMocks()
})

test.each([
  ['no clue', null, 'attempt-1', true],
  ['no selected attempt', clue, null, true],
  ['attempt not loaded', clue, 'attempt-1', false],
] as const)('does not load candidates when there is %s', async (_condition, selectedClue, attemptId, attemptLoaded) => {
  const { result } = renderHook(() => usePuzzleCandidateAnswers('puzzle-1', attemptId, selectedClue, attemptLoaded))

  await act(async () => {
    await result.current.load()
  })

  expect(apiClient.postCandidateAnswers).not.toHaveBeenCalled()
})

test('uses a fallback message when candidate loading rejects without an Error', async () => {
  vi.mocked(apiClient.postCandidateAnswers).mockRejectedValueOnce('offline')
  const { result } = renderHook(() => usePuzzleCandidateAnswers('puzzle-1', 'attempt-1', clue, true))

  await act(async () => {
    await result.current.load()
  })

  expect(result.current.error).toBe('Unable to load candidate answers.')
})
