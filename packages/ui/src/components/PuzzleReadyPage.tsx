import { Sparkles } from 'lucide-react'
import type { Puzzle, PuzzleAnswer, PuzzleAttemptSummary, PuzzleClue } from '../apiClient'
import { PuzzleAnswerInput } from './PuzzleAnswerInput'
import { PuzzleAttemptSelector } from './PuzzleAttemptSelector'
import { PuzzleClueList } from './PuzzleClueList'
import { PuzzleGrid } from './PuzzleGrid'
import type { AttemptLoadStatus, PuzzleDraftAnswer } from './puzzlePageHelpers'

type Props = Readonly<{
  puzzle: Puzzle
  selectedClue: PuzzleClue | null
  selectedWord: Puzzle['words'][number] | undefined
  selectedSavedAnswer: PuzzleAnswer | undefined
  selectedAttemptId: string | null
  selectedAttempt: PuzzleAttemptSummary | null
  selectedAttemptNumber: number | null
  attemptSummaries: PuzzleAttemptSummary[]
  attemptSummariesState: 'loading' | 'error' | 'ready'
  attemptSummariesError: string
  attemptHistoryOpen: boolean
  creatingAttempt: boolean
  attemptError: string
  attemptLoadStatus: AttemptLoadStatus
  attemptLoadError: string
  savedAnswers: PuzzleAnswer[]
  displayedSavedAnswers: PuzzleAnswer[]
  draftAnswers: PuzzleDraftAnswer[]
  answerStatus: string
  displayedCharacters: string[]
  crossingCharacters: Map<string, string>
  hasAnswerDraft: boolean
  savingAnswer: boolean
  answerError: string
  focusKey: string
  canSubmit: boolean
  onToggleHistory: () => void
  onCreateAttempt: () => void
  onSelectAttempt: (attemptId: string) => void
  onRetryAttempt: (attemptId: string) => void
  onChangeAnswer: (index: number, value: string) => void
  onClearAnswer: () => void
  onSubmitAnswer: () => void
  onSelectClue: (clue: PuzzleClue) => void
}>

export function PuzzleReadyPage({
  puzzle,
  selectedClue,
  selectedWord,
  selectedSavedAnswer,
  selectedAttemptId,
  selectedAttempt,
  selectedAttemptNumber,
  attemptSummaries,
  attemptSummariesState,
  attemptSummariesError,
  attemptHistoryOpen,
  creatingAttempt,
  attemptError,
  attemptLoadStatus,
  attemptLoadError,
  savedAnswers,
  displayedSavedAnswers,
  draftAnswers,
  answerStatus,
  displayedCharacters,
  crossingCharacters,
  hasAnswerDraft,
  savingAnswer,
  answerError,
  focusKey,
  canSubmit,
  onToggleHistory,
  onCreateAttempt,
  onSelectAttempt,
  onRetryAttempt,
  onChangeAnswer,
  onClearAnswer,
  onSubmitAnswer,
  onSelectClue,
}: Props) {
  return (
    <>
      <header className="puzzle-heading">
        <div>
          <h1>{puzzle.name || 'Untitled puzzle'}</h1>
          <p>{puzzle.grid.numberOfColumns} &times; {puzzle.grid.numberOfRows}<span aria-hidden="true"> / </span>{puzzle.clues.length} clues</p>
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
        selectedAttemptNumber={selectedAttemptNumber}
        savedAnswerCount={savedAnswers.length}
        onToggleHistory={onToggleHistory}
        onCreateAttempt={onCreateAttempt}
        onSelectAttempt={onSelectAttempt}
        onRetryAttempt={onRetryAttempt}
      />
      <div className="puzzle-workspace">
        <section className="puzzle-board-section" aria-labelledby="grid-heading">
          <div className="puzzle-section-heading"><h2 id="grid-heading">Grid</h2><button className="upload-button import-button" type="button" disabled title="Automatic solving is not available yet"><Sparkles size={15} aria-hidden="true" /> Auto-solve</button></div>
          <PuzzleGrid puzzle={puzzle} selectedClue={selectedClue} answers={displayedSavedAnswers} drafts={draftAnswers} />
        </section>
        <section className="puzzle-clues-section" aria-label="Puzzle clues">
          {selectedClue && (
            <PuzzleAnswerInput
              clue={selectedClue}
              word={selectedWord}
              savedAnswer={selectedSavedAnswer}
              status={answerStatus}
              characters={displayedCharacters}
              crossingCharacters={crossingCharacters}
              hasDraft={hasAnswerDraft}
              attemptSelected={Boolean(selectedAttemptId)}
              saving={savingAnswer}
              error={answerError}
              focusKey={focusKey}
              canSubmit={canSubmit}
              onChange={onChangeAnswer}
              onClear={onClearAnswer}
              onSubmit={onSubmitAnswer}
            />
          )}
          <PuzzleClueList
            clues={puzzle.clues}
            savedAnswers={savedAnswers}
            selectedClue={selectedClue}
            onSelect={onSelectClue}
          />
        </section>
      </div>
    </>
  )
}
