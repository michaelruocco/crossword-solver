import { ArrowLeft } from 'lucide-react'
import type { PuzzleState } from './usePuzzlePageRequests'

export function PuzzlePageStatus({ state, onRetry }: Readonly<{
  state: Exclude<PuzzleState, { status: 'ready' }>
  onRetry: () => void
}>) {
  return (
    <main className="main-content puzzle-page">
      <a className="puzzle-back" href="/"><ArrowLeft size={16} aria-hidden="true" /> Puzzle library</a>
      {state.status === 'loading'
        ? <output className="state-panel">Loading puzzle...</output>
        : (
          <div className="state-panel" role="alert">
            <h1>Could not load puzzle</h1>
            <p>{state.message}</p>
            <button type="button" className="retry-button" onClick={onRetry}>Try again</button>
          </div>
        )}
    </main>
  )
}
