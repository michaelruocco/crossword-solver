import { useEffect, useState } from 'react'
import { ArrowLeft, Sparkles } from 'lucide-react'
import { apiClient, type Puzzle, type PuzzleAnswer, type PuzzleAttempt, type PuzzleAttemptSummary, type PuzzleClue } from '../apiClient'
import { PuzzleAnswerInput } from './PuzzleAnswerInput'
import { PuzzleAttemptSelector } from './PuzzleAttemptSelector'
import { PuzzleClueList } from './PuzzleClueList'
import { PuzzleGrid } from './PuzzleGrid'
import {
  clueAnswerId,
  getAnswerCharacterMap,
  getAnswerStatus,
  getAttemptLoadStatus,
  getDisplayedAnswerCharacters,
  getPuzzleDraftAnswers,
  updateDraftAnswers,
} from './puzzlePageHelpers'

type PuzzleState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; puzzle: Puzzle }
type AttemptDetailsState =
  | { attemptId: string; status: 'loading' }
  | { attemptId: string; status: 'error'; message: string }
  | { attemptId: string; status: 'ready'; attempt: PuzzleAttempt }

export function PuzzlePage({ puzzleId }: Readonly<{ puzzleId: string }>) {
  const [state, setState] = useState<PuzzleState>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)
  const [selectedClue, setSelectedClue] = useState<PuzzleClue | null>(null)
  const [answerDrafts, setAnswerDrafts] = useState<Record<string, string[]>>({})
  const [attemptSummaries, setAttemptSummaries] = useState<PuzzleAttemptSummary[]>([])
  const [attemptSummariesState, setAttemptSummariesState] = useState<'loading' | 'error' | 'ready'>('loading')
  const [attemptSummariesError, setAttemptSummariesError] = useState('')
  const [selectedAttemptId, setSelectedAttemptId] = useState<string | null>(null)
  const [attemptDetails, setAttemptDetails] = useState<AttemptDetailsState | null>(null)
  const [attemptReloadKey, setAttemptReloadKey] = useState(0)
  const [attemptHistoryOpen, setAttemptHistoryOpen] = useState(false)
  const [creatingAttempt, setCreatingAttempt] = useState(false)
  const [savingAnswer, setSavingAnswer] = useState(false)
  const [attemptError, setAttemptError] = useState('')
  const [answerError, setAnswerError] = useState('')
  const selectedClueKey = selectedClue
    ? `${selectedAttemptId ?? 'unselected'}:${selectedClue.direction}-${selectedClue.id}`
    : ''
  const answerDraft = answerDrafts[selectedClueKey] ?? []
  const hasAnswerDraft = answerDraft.some(Boolean)
  const selectedAttempt = attemptSummaries.find((summary) => summary.id === selectedAttemptId) ?? null
  const loadedAttempt = attemptDetails?.status === 'ready' && attemptDetails.attemptId === selectedAttemptId
    ? attemptDetails.attempt
    : null
  const savedAnswers = loadedAttempt?.answers ?? []
  const selectedSavedAnswer = selectedClue
    ? savedAnswers.find((answer) => answer.id === clueAnswerId(selectedClue))
    : undefined
  const selectedWord = selectedClue && state.status === 'ready'
    ? state.puzzle.words.find((word) => word.id === selectedClue.id && word.direction === selectedClue.direction)
    : undefined
  const answerLength = selectedClue
    ? selectedWord?.length ?? selectedClue.lengths.reduce((length, part) => length + part, 0)
    : 0
  const puzzle = state.status === 'ready' ? state.puzzle : null
  const draftAnswers = getPuzzleDraftAnswers(puzzle, selectedAttemptId, answerDrafts, savedAnswers)
  const displayedSavedAnswers = savedAnswers.filter((answer) => !draftAnswers.some((draft) => draft.id === answer.id))
  const selectedCrossingCharacters = puzzle && selectedClue
    ? getAnswerCharacterMap(puzzle, displayedSavedAnswers, draftAnswers, clueAnswerId(selectedClue))
    : new Map<string, string>()
  const displayedCharacters = getDisplayedAnswerCharacters(
    answerLength,
    selectedWord,
    selectedCrossingCharacters,
    answerDraft,
    selectedSavedAnswer,
  )
  const displayedAnswer = displayedCharacters.join('')
  const answerStatus = getAnswerStatus(hasAnswerDraft, selectedSavedAnswer)

  const updateAnswerDraft = (index: number, value: string) => {
    setAnswerError('')
    setAnswerDrafts((drafts) => updateDraftAnswers(drafts, selectedClueKey, answerLength, index, value))
  }

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
  }, [puzzleId, selectedAttemptId, attemptReloadKey])

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

  useEffect(() => {
    const controller = new AbortController()
    apiClient.getAttemptSummaries(puzzleId, controller.signal)
      .then((summaries) => {
        if (!controller.signal.aborted) {
          setAttemptSummaries(summaries)
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
  }, [puzzleId])

  const retry = () => {
    setState({ status: 'loading' })
    setReloadKey((key) => key + 1)
  }

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

  const retryAttempt = (attemptId: string) => {
    setAttemptDetails({ attemptId, status: 'loading' })
    setAttemptReloadKey((key) => key + 1)
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
      setAttemptSummaries((summaries) => [summary, ...summaries.filter((existing) => existing.id !== summary.id)])
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

  const submitAnswer = async (attempt: PuzzleAttempt, clue: PuzzleClue) => {
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

  const submitAnswerAction = loadedAttempt && selectedClue
    ? () => void submitAnswer(loadedAttempt, selectedClue)
    : undefined
  const attemptLoadStatus = getAttemptLoadStatus(selectedAttempt, attemptDetails)
  const attemptLoadError = attemptDetails?.status === 'error' && attemptDetails.attemptId === selectedAttemptId
    ? attemptDetails.message
    : ''

  return (
    <main className="main-content puzzle-page">
      <a className="puzzle-back" href="/"><ArrowLeft size={16} aria-hidden="true" /> Puzzle library</a>
      {state.status === 'loading' && <output className="state-panel">Loading puzzle...</output>}
      {state.status === 'error' && (
        <div className="state-panel" role="alert">
          <h1>Could not load puzzle</h1>
          <p>{state.message}</p>
          <button type="button" className="retry-button" onClick={retry}>Try again</button>
        </div>
      )}
      {state.status === 'ready' && (
        <>
          <header className="puzzle-heading">
            <div>
              <h1>{state.puzzle.name || 'Untitled puzzle'}</h1>
              <p>{state.puzzle.grid.numberOfColumns} &times; {state.puzzle.grid.numberOfRows}<span aria-hidden="true"> / </span>{state.puzzle.clues.length} clues</p>
            </div>
            <span className="puzzle-view-label">Puzzle preview</span>
          </header>
          <PuzzleAttemptSelector
            summaries={attemptSummaries}
            summariesState={attemptSummariesState}
            summariesError={attemptSummariesError}
            selectedAttemptId={selectedAttemptId}
            historyOpen={attemptHistoryOpen}
            creatingAttempt={creatingAttempt}
            attemptError={attemptError}
            attemptLoadStatus={attemptLoadStatus}
            attemptLoadError={attemptLoadError}
            selectedAttempt={selectedAttempt}
            savedAnswerCount={savedAnswers.length}
            onToggleHistory={() => setAttemptHistoryOpen((open) => !open)}
            onCreateAttempt={() => void createAttempt()}
            onSelectAttempt={selectAttempt}
            onRetryAttempt={retryAttempt}
          />
          <div className="puzzle-workspace">
            <section className="puzzle-board-section" aria-labelledby="grid-heading">
              <div className="puzzle-section-heading"><h2 id="grid-heading">Grid</h2><button className="upload-button import-button" type="button" disabled title="Automatic solving is not available yet"><Sparkles size={15} aria-hidden="true" /> Auto-solve</button></div>
              <PuzzleGrid puzzle={state.puzzle} selectedClue={selectedClue} answers={displayedSavedAnswers} drafts={draftAnswers} />
            </section>
            <section className="puzzle-clues-section" aria-label="Puzzle clues">
              {selectedClue && (
                <PuzzleAnswerInput
                  clue={selectedClue}
                  word={selectedWord}
                  savedAnswer={selectedSavedAnswer}
                  status={answerStatus}
                  characters={displayedCharacters}
                  crossingCharacters={selectedCrossingCharacters}
                  hasDraft={hasAnswerDraft}
                  attemptSelected={Boolean(selectedAttemptId)}
                  saving={savingAnswer}
                  error={answerError}
                  focusKey={`${selectedClueKey}:${loadedAttempt?.id ?? ''}`}
                  canSubmit={Boolean(submitAnswerAction) && displayedCharacters.length > 0 && displayedCharacters.every(Boolean)}
                  onChange={updateAnswerDraft}
                  onClear={() => {
                    setAnswerError('')
                    setAnswerDrafts((drafts) => {
                      const updatedDrafts = { ...drafts }
                      delete updatedDrafts[selectedClueKey]
                      return updatedDrafts
                    })
                  }}
                  onSubmit={() => submitAnswerAction?.()}
                />
              )}
              <PuzzleClueList
                clues={state.puzzle.clues}
                savedAnswers={savedAnswers}
                selectedClue={selectedClue}
                onSelect={(clue) => {
                  setSelectedClue(clue)
                  setAnswerError('')
                }}
              />
            </section>
          </div>
        </>
      )}
    </main>
  )
}