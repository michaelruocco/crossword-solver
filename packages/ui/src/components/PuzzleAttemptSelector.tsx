import { History, Plus } from 'lucide-react'
import type { PuzzleAttemptSummary } from '../apiClient'

type Props = Readonly<{
  summaries: PuzzleAttemptSummary[]
  summariesState: 'loading' | 'error' | 'ready'
  summariesError: string
  selectedAttemptId: string | null
  historyOpen: boolean
  creatingAttempt: boolean
  attemptError: string
  attemptLoadStatus: 'loading' | 'error' | null
  attemptLoadError: string
  selectedAttempt: PuzzleAttemptSummary | null
  savedAnswerCount: number
  onToggleHistory: () => void
  onCreateAttempt: () => void
  onSelectAttempt: (attemptId: string) => void
  onRetryAttempt: () => void
}>

export function PuzzleAttemptSelector({
  summaries,
  summariesState,
  summariesError,
  selectedAttemptId,
  historyOpen,
  creatingAttempt,
  attemptError,
  attemptLoadStatus,
  attemptLoadError,
  selectedAttempt,
  savedAnswerCount,
  onToggleHistory,
  onCreateAttempt,
  onSelectAttempt,
  onRetryAttempt,
}: Props) {
  return (
    <section className="attempt-toolbar" aria-label="Puzzle attempts">
      <div className="attempt-context"><History size={18} aria-hidden="true" /><strong>Attempts</strong><span aria-live="polite">{selectedAttempt ? `${selectedAttempt.answerCount} of ${selectedAttempt.clueCount} clues answered` : `${summaries.length} available`}</span></div>
      <div className="attempt-actions">
        <button type="button" className="upload-button import-button" aria-expanded={historyOpen} aria-controls="attempt-history" onClick={onToggleHistory}><History size={15} aria-hidden="true" /> Previous attempts</button>
        <button type="button" className="upload-button" disabled={creatingAttempt} onClick={onCreateAttempt}><Plus size={16} aria-hidden="true" /> {creatingAttempt ? 'Creating...' : 'New attempt'}</button>
      </div>
      {attemptError && <p className="attempt-error" role="alert">{attemptError}</p>}
      {historyOpen && (
        <section id="attempt-history" className="attempt-history" aria-label="Previous attempts">
          {summariesState === 'loading' && <output>Loading attempts...</output>}
          {summariesState === 'error' && <p role="alert">{summariesError}</p>}
          {summariesState === 'ready' && summaries.length === 0 && <p>No attempts yet.</p>}
          {summaries.length > 0 && (
            <div className="attempt-history-list">
              {summaries.map((summary, index) => (
                <button
                  key={summary.id}
                  type="button"
                  className="attempt-history-item"
                  aria-pressed={selectedAttemptId === summary.id}
                  onClick={() => onSelectAttempt(summary.id)}
                >
                  <strong>Attempt {index + 1}</strong>
                  <time dateTime={summary.createdAt}>{new Date(summary.createdAt).toLocaleString()}</time>
                  <span>{summary.answerCount} of {summary.clueCount} answered</span>
                </button>
              ))}
            </div>
          )}
        </section>
      )}
      {selectedAttempt && (
        <output className="attempt-status" aria-label="Selected attempt status">
          <strong>Selected attempt</strong>
          <span>{selectedAttempt.answerCount} of {selectedAttempt.clueCount} clues answered</span>
          <span>{selectedAttempt.solving ? 'Solving' : 'Not solving'}</span>
          {attemptLoadStatus === 'loading' && <span className="attempt-status-note">Loading saved answers...</span>}
          {attemptLoadStatus === 'error' && (
            <span className="attempt-status-note" role="alert">
              {attemptLoadError}{' '}
              <button type="button" className="inline-button" onClick={onRetryAttempt}>Retry</button>
            </span>
          )}
          {attemptLoadStatus === null && <span className="attempt-status-note">{savedAnswerCount} saved {savedAnswerCount === 1 ? 'answer' : 'answers'} loaded.</span>}
        </output>
      )}
    </section>
  )
}
