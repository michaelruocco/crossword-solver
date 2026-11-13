import { useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import type { PuzzleClue } from '../apiClient'
import { PuzzleReadyPage } from './PuzzleReadyPage'
import {
  canSubmitAnswer,
  getAnswerStatus,
  getAnswerLength,
  getAttemptLoadError,
  getAttemptLoadStatus,
  getDisplayedAnswerCharacters,
  getLoadedAttempt,
  getPuzzleFromState,
  getPuzzleDraftAnswers,
  getSelectedAttempt,
  getSelectedAttemptNumber,
  getSelectedCrossingCharacters,
  getSelectedSavedAnswer,
  getSelectedWord,
  updateDraftAnswers,
} from './puzzlePageHelpers'
import { usePuzzlePageActions } from './usePuzzlePageActions'
import { useAttemptDetailsRequest, useAttemptSummariesRequest, usePuzzleRequest } from './usePuzzlePageRequests'

export function PuzzlePage({ puzzleId }: Readonly<{ puzzleId: string }>) {
  const { state, retry } = usePuzzleRequest(puzzleId)
  const [selectedClue, setSelectedClue] = useState<PuzzleClue | null>(null)
  const [answerDrafts, setAnswerDrafts] = useState<Record<string, string[]>>({})
  const [selectedAttemptId, setSelectedAttemptId] = useState<string | null>(null)
  const [attemptHistoryOpen, setAttemptHistoryOpen] = useState(false)
  const {
    attemptSummaries,
    setAttemptSummaries,
    attemptSummariesState,
    setAttemptSummariesState,
    attemptSummariesError,
    setAttemptSummariesError,
  } = useAttemptSummariesRequest(puzzleId, setSelectedAttemptId)
  const { attemptDetails, setAttemptDetails, retryAttempt } = useAttemptDetailsRequest(
    puzzleId,
    selectedAttemptId,
    setAttemptSummaries,
  )
  const selectedClueKey = selectedClue
    ? `${selectedAttemptId ?? 'unselected'}:${selectedClue.direction}-${selectedClue.id}`
    : ''
  const answerDraft = answerDrafts[selectedClueKey] ?? []
  const hasAnswerDraft = answerDraft.some(Boolean)
  const selectedAttempt = getSelectedAttempt(attemptSummaries, selectedAttemptId)
  const selectedAttemptNumber = getSelectedAttemptNumber(attemptSummaries, selectedAttempt)
  const loadedAttempt = getLoadedAttempt(attemptDetails, selectedAttemptId)
  const savedAnswers = loadedAttempt?.answers ?? []
  const selectedSavedAnswer = getSelectedSavedAnswer(selectedClue, savedAnswers)
  const puzzle = getPuzzleFromState(state)
  const selectedWord = getSelectedWord(puzzle, selectedClue)
  const answerLength = getAnswerLength(selectedClue, selectedWord)
  const draftAnswers = getPuzzleDraftAnswers(puzzle, selectedAttemptId, answerDrafts, savedAnswers)
  const displayedSavedAnswers = savedAnswers.filter((answer) => !draftAnswers.some((draft) => draft.id === answer.id))
  const selectedCrossingCharacters = getSelectedCrossingCharacters(
    puzzle,
    selectedClue,
    displayedSavedAnswers,
    draftAnswers,
  )
  const displayedCharacters = getDisplayedAnswerCharacters(
    answerLength,
    selectedWord,
    selectedCrossingCharacters,
    answerDraft,
    selectedSavedAnswer,
  )
  const displayedAnswer = displayedCharacters.join('')
  const answerStatus = getAnswerStatus(hasAnswerDraft, selectedSavedAnswer)

  const {
    creatingAttempt,
    savingAnswer,
    attemptError,
    answerError,
    setAnswerError,
    selectAttempt,
    createAttempt,
    submitAnswer,
  } = usePuzzlePageActions({
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
  })

  const updateAnswerDraft = (index: number, value: string) => {
    setAnswerError('')
    setAnswerDrafts((drafts) => updateDraftAnswers(drafts, selectedClueKey, answerLength, index, value))
  }

  const clearAnswerDraft = () => {
    setAnswerError('')
    setAnswerDrafts((drafts) => {
      const updatedDrafts = { ...drafts }
      delete updatedDrafts[selectedClueKey]
      return updatedDrafts
    })
  }

  const selectClue = (clue: PuzzleClue) => {
    setSelectedClue(clue)
    setAnswerError('')
  }

  const submitAnswerAction = loadedAttempt && selectedClue
    ? () => void submitAnswer(loadedAttempt, selectedClue)
    : undefined
  const attemptLoadStatus = getAttemptLoadStatus(selectedAttempt, attemptDetails)
  const attemptLoadError = getAttemptLoadError(attemptDetails, selectedAttemptId)

  if (state.status === 'loading') {
    return (
      <main className="main-content puzzle-page">
        <a className="puzzle-back" href="/"><ArrowLeft size={16} aria-hidden="true" /> Puzzle library</a>
        <output className="state-panel">Loading puzzle...</output>
      </main>
    )
  }

  if (state.status === 'error') {
    return (
      <main className="main-content puzzle-page">
        <a className="puzzle-back" href="/"><ArrowLeft size={16} aria-hidden="true" /> Puzzle library</a>
        <div className="state-panel" role="alert">
          <h1>Could not load puzzle</h1>
          <p>{state.message}</p>
          <button type="button" className="retry-button" onClick={retry}>Try again</button>
        </div>
      </main>
    )
  }

  return (
    <main className="main-content puzzle-page">
      <a className="puzzle-back" href="/"><ArrowLeft size={16} aria-hidden="true" /> Puzzle library</a>
      <PuzzleReadyPage
        puzzle={state.puzzle}
        selectedClue={selectedClue}
        selectedWord={selectedWord}
        selectedSavedAnswer={selectedSavedAnswer}
        selectedAttemptId={selectedAttemptId}
        selectedAttempt={selectedAttempt}
        selectedAttemptNumber={selectedAttemptNumber}
        attemptSummaries={attemptSummaries}
        attemptSummariesState={attemptSummariesState}
        attemptSummariesError={attemptSummariesError}
        attemptHistoryOpen={attemptHistoryOpen}
        creatingAttempt={creatingAttempt}
        attemptError={attemptError}
        attemptLoadStatus={attemptLoadStatus}
        attemptLoadError={attemptLoadError}
        savedAnswers={savedAnswers}
        displayedSavedAnswers={displayedSavedAnswers}
        draftAnswers={draftAnswers}
        answerStatus={answerStatus}
        displayedCharacters={displayedCharacters}
        crossingCharacters={selectedCrossingCharacters}
        hasAnswerDraft={hasAnswerDraft}
        savingAnswer={savingAnswer}
        answerError={answerError}
        focusKey={`${selectedClueKey}:${loadedAttempt?.id ?? ''}`}
        canSubmit={canSubmitAnswer(Boolean(submitAnswerAction), displayedCharacters)}
        onToggleHistory={() => setAttemptHistoryOpen((open) => !open)}
        onCreateAttempt={() => void createAttempt()}
        onSelectAttempt={selectAttempt}
        onRetryAttempt={retryAttempt}
        onChangeAnswer={updateAnswerDraft}
        onClearAnswer={clearAnswerDraft}
        onSubmitAnswer={() => submitAnswerAction?.()}
        onSelectClue={selectClue}
      />
    </main>
  )
}