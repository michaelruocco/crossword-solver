import { useState, type Dispatch, type SetStateAction } from 'react'
import { apiClient, type PuzzleAnswer, type PuzzleAttempt, type PuzzleAttemptSummary, type PuzzleClue } from '../apiClient'
import { clueAnswerId, sortAttemptsNewestFirst } from './puzzlePageHelpers'
import type { AttemptDetailsState } from './usePuzzlePageRequests'

type StateSetter<T> = Dispatch<SetStateAction<T>>

type PuzzlePageActionOptions = {
  puzzleId: string
  selectedAttemptId: string | null
  setSelectedAttemptId: StateSetter<string | null>
  setAttemptSummaries: StateSetter<PuzzleAttemptSummary[]>
  setAttemptSummariesState: StateSetter<'loading' | 'error' | 'ready'>
  setAttemptSummariesError: StateSetter<string>
  setAttemptDetails: StateSetter<AttemptDetailsState | null>
  setAttemptHistoryOpen: StateSetter<boolean>
  setSelectedClue: StateSetter<PuzzleClue | null>
  setAnswerDrafts: StateSetter<Record<string, string[]>>
  selectedClueKey: string
  displayedAnswer: string
}

export function usePuzzlePageActions({
  puzzleId,
  selectedAttemptId,
  setSelectedAttemptId,
  setAttemptSummaries,
  setAttemptSummariesState,
  setAttemptSummariesError,
  setAttemptDetails,
  setAttemptHistoryOpen,
  setSelectedClue,
  setAnswerDrafts,
  selectedClueKey,
  displayedAnswer,
}: PuzzlePageActionOptions) {
  const [creatingAttempt, setCreatingAttempt] = useState(false)
  const [savingAnswer, setSavingAnswer] = useState(false)
  const [attemptError, setAttemptError] = useState('')
  const [answerError, setAnswerError] = useState('')

  const selectAttempt = (attemptId: string) => {
    if (selectedAttemptId !== attemptId) {
      setAttemptDetails({ attemptId, status: 'loading' })
    }
    setSelectedAttemptId(attemptId)
    setAttemptHistoryOpen(false)
    setAttemptError('')
    setAnswerError('')
    setSelectedClue(null)
  }

  const createAttempt = async () => {
    setCreatingAttempt(true)
    setAttemptError('')
    try {
      const created = await apiClient.createAttempt(puzzleId)
      const summary = {
        id: created.id,
        createdAt: created.createdAt,
        solving: created.solving,
        answerCount: created.answerCount,
        clueCount: created.puzzle.clues.length,
      }
      setAttemptSummaries((summaries) => sortAttemptsNewestFirst([
        summary,
        ...summaries.filter((existing) => existing.id !== summary.id),
      ]))
      setAttemptSummariesState('ready')
      setAttemptSummariesError('')
      setAnswerDrafts((drafts) => {
        const updatedDrafts = { ...drafts }
        for (const [key, value] of Object.entries(drafts)) {
          if (key.startsWith('unselected:')) {
            updatedDrafts[`${summary.id}:${key.slice('unselected:'.length)}`] = value
            delete updatedDrafts[key]
          }
        }
        return updatedDrafts
      })
      setSelectedAttemptId(summary.id)
      setAttemptDetails({ attemptId: summary.id, status: 'loading' })
      setAttemptHistoryOpen(false)
    } catch (error) {
      setAttemptError(error instanceof Error ? error.message : 'Unable to create puzzle attempt.')
    } finally {
      setCreatingAttempt(false)
    }
  }

  const submitAnswer = async (
    attempt: PuzzleAttempt,
    clue: PuzzleClue,
  ) => {
    setSavingAnswer(true)
    setAnswerError('')
    const answer: PuzzleAnswer = {
      id: clueAnswerId(clue),
      value: displayedAnswer.trim().toUpperCase(),
    }
    try {
      const updatedAttempt = await apiClient.postAttemptAnswer(puzzleId, attempt.id, answer)
      setAttemptDetails((details) => details?.attemptId === updatedAttempt.id
        ? { attemptId: updatedAttempt.id, status: 'ready', attempt: updatedAttempt }
        : details)
      setAttemptSummaries((summaries) => summaries.map((summary) => (
        summary.id === updatedAttempt.id ? { ...summary, answerCount: updatedAttempt.answerCount } : summary
      )))
      setAnswerDrafts((drafts) => {
        const { [selectedClueKey]: _submittedDraft, ...remainingDrafts } = drafts
        return remainingDrafts
      })
    } catch (error) {
      setAnswerError(error instanceof Error ? error.message : 'Unable to save attempt answer.')
    } finally {
      setSavingAnswer(false)
    }
  }

  return {
    creatingAttempt,
    savingAnswer,
    attemptError,
    answerError,
    setAnswerError,
    selectAttempt,
    createAttempt,
    submitAnswer,
  }
}
