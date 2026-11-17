import { useState } from 'react'
import { apiClient, type PuzzleCandidateAnswer, type PuzzleClue } from '../apiClient'
import { clueAnswerId } from './puzzlePageHelpers'

type CandidateAnswersState = {
  key: string
  status: 'loading' | 'ready' | 'error'
  answers: PuzzleCandidateAnswer[]
  error: string
}

export function usePuzzleCandidateAnswers(
  puzzleId: string,
  attemptId: string | null,
  clue: PuzzleClue | null,
  attemptLoaded: boolean,
) {
  const [state, setState] = useState<CandidateAnswersState | null>(null)
  const key = clue && attemptId ? `${attemptId}:${clue.direction}-${clue.id}` : ''
  const selectedState = state?.key === key ? state : null

  const load = async () => {
    if (!clue || !attemptId || !attemptLoaded) return

    setState({ key, status: 'loading', answers: [], error: '' })
    try {
      const result = await apiClient.postCandidateAnswers(puzzleId, attemptId, clueAnswerId(clue))
      setState({ key, status: 'ready', answers: result.answers, error: '' })
    } catch (error) {
      setState({
        key,
        status: 'error',
        answers: [],
        error: error instanceof Error ? error.message : 'Unable to load candidate answers.',
      })
    }
  }

  return {
    answers: selectedState?.status === 'ready' ? selectedState.answers : null,
    loading: selectedState?.status === 'loading',
    error: selectedState?.status === 'error' ? selectedState.error : '',
    load,
  }
}
