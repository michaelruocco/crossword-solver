import { useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import { apiClient, type Puzzle, type PuzzleAttempt, type PuzzleAttemptSummary } from '../apiClient'
import { mergeAttemptSummaries, sortAttemptsOldestFirst } from './puzzlePageHelpers'

export type PuzzleState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; puzzle: Puzzle }
export type AttemptDetailsState =
  | { attemptId: string; status: 'loading' }
  | { attemptId: string; status: 'error'; message: string }
  | { attemptId: string; status: 'ready'; attempt: PuzzleAttempt }

type StateSetter<T> = Dispatch<SetStateAction<T>>

export function usePuzzleRequest(puzzleId: string) {
  const [state, setState] = useState<PuzzleState>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    apiClient.getPuzzle(puzzleId, controller.signal)
      .then((puzzle) => {
        if (!controller.signal.aborted) setState({ status: 'ready', puzzle })
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setState({ status: 'error', message: error instanceof Error ? error.message : 'Unable to load puzzle.' })
        }
      })
    return () => controller.abort()
  }, [puzzleId, reloadKey])

  const retry = () => {
    setState({ status: 'loading' })
    setReloadKey((key) => key + 1)
  }

  return { state, retry }
}

export function useAttemptSummariesRequest(
  puzzleId: string,
  setSelectedAttemptId: StateSetter<string | null>,
) {
  const [attemptSummaries, setAttemptSummaries] = useState<PuzzleAttemptSummary[]>([])
  const [attemptSummariesState, setAttemptSummariesState] = useState<'loading' | 'error' | 'ready'>('loading')
  const [attemptSummariesError, setAttemptSummariesError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    apiClient.getAttemptSummaries(puzzleId, controller.signal)
      .then((summaries) => {
        if (!controller.signal.aborted) {
          const orderedSummaries = sortAttemptsOldestFirst(summaries)
          setAttemptSummaries((existing) => mergeAttemptSummaries(existing, orderedSummaries))
          setSelectedAttemptId((current) => current ?? orderedSummaries.at(-1)?.id ?? null)
          setAttemptSummariesState('ready')
        }
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setAttemptSummariesError(error instanceof Error ? error.message : 'Unable to load attempt summaries.')
          setAttemptSummariesState('error')
        }
      })
    return () => controller.abort()
  }, [puzzleId, setSelectedAttemptId])

  return {
    attemptSummaries,
    setAttemptSummaries,
    attemptSummariesState,
    setAttemptSummariesState,
    attemptSummariesError,
    setAttemptSummariesError,
  }
}

export function useAttemptDetailsRequest(
  puzzleId: string,
  selectedAttemptId: string | null,
  setAttemptSummaries: StateSetter<PuzzleAttemptSummary[]>,
) {
  const [attemptDetails, setAttemptDetails] = useState<AttemptDetailsState | null>(null)
  const [attemptReloadKey, setAttemptReloadKey] = useState(0)

  useEffect(() => {
    if (!selectedAttemptId) return

    const controller = new AbortController()
    apiClient.getAttempt(puzzleId, selectedAttemptId, controller.signal)
      .then((attempt) => {
        if (!controller.signal.aborted) {
          setAttemptDetails({ attemptId: selectedAttemptId, status: 'ready', attempt })
          setAttemptSummaries((summaries) => summaries.map((summary) => (
            summary.id === attempt.id ? { ...summary, answerCount: attempt.answerCount } : summary
          )))
        }
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setAttemptDetails({
            attemptId: selectedAttemptId,
            status: 'error',
            message: error instanceof Error ? error.message : 'Unable to load puzzle attempt.',
          })
        }
      })
    return () => controller.abort()
  }, [puzzleId, selectedAttemptId, attemptReloadKey, setAttemptSummaries])

  const retryAttempt = (attemptId: string) => {
    setAttemptDetails({ attemptId, status: 'loading' })
    setAttemptReloadKey((key) => key + 1)
  }

  return { attemptDetails, setAttemptDetails, retryAttempt }
}
