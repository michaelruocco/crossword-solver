import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, ArrowDown, Eraser, History, Plus, Send, Sparkles, Trash2 } from 'lucide-react'
import { apiClient, type Puzzle, type PuzzleAnswer, type PuzzleAttempt, type PuzzleAttemptSummary, type PuzzleClue } from '../apiClient'

type PuzzleState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; puzzle: Puzzle }
type AttemptDetailsState =
  | { attemptId: string; status: 'loading' }
  | { attemptId: string; status: 'error'; message: string }
  | { attemptId: string; status: 'ready'; attempt: PuzzleAttempt }

export function PuzzlePage({ puzzleId }: Readonly<{ puzzleId: string }>) {
  const [state, setState] = useState<PuzzleState>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)
  const [selectedClue, setSelectedClue] = useState<PuzzleClue | null>(null)
  const [answerDrafts, setAnswerDrafts] = useState<Record<string, string>>({})
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
  const hasAnswerDraft = Object.hasOwn(answerDrafts, selectedClueKey)
  const answerDraft = answerDrafts[selectedClueKey] ?? ''
  const selectedAttempt = attemptSummaries.find((summary) => summary.id === selectedAttemptId) ?? null
  const loadedAttempt = attemptDetails?.status === 'ready' && attemptDetails.attemptId === selectedAttemptId
    ? attemptDetails.attempt
    : null
  const savedAnswers = loadedAttempt?.answers ?? []
  const selectedSavedAnswer = selectedClue
    ? savedAnswers.find((answer) => answer.id === clueAnswerId(selectedClue))
    : undefined
  const displayedAnswer = hasAnswerDraft ? answerDraft : selectedSavedAnswer?.value ?? ''
  let answerStatus = 'Not submitted'
  if (selectedSavedAnswer) answerStatus = 'Saved answer'
  if (hasAnswerDraft) answerStatus = 'Unsaved draft'

  const updateAnswerDraft = (value: string) => {
    setAnswerError('')
    setAnswerDrafts((drafts) => {
      if (value) return { ...drafts, [selectedClueKey]: value }
      const updatedDrafts = { ...drafts }
      delete updatedDrafts[selectedClueKey]
      return updatedDrafts
    })
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

  const submitAnswer = async () => {
    if (!loadedAttempt || !selectedClue || !displayedAnswer.trim() || savingAnswer) return

    setSavingAnswer(true)
    setAnswerError('')
    const answer: PuzzleAnswer = {
      id: clueAnswerId(selectedClue),
      value: displayedAnswer.trim().toUpperCase(),
    }
    try {
      const updatedAttempt = await apiClient.postAttemptAnswer(puzzleId, loadedAttempt.id, answer)
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
          <section className="attempt-toolbar" aria-label="Puzzle attempts">
            <div className="attempt-context"><History size={18} aria-hidden="true" /><strong>Attempts</strong><span aria-live="polite">{selectedAttempt ? `${selectedAttempt.answerCount} of ${selectedAttempt.clueCount} clues answered` : `${attemptSummaries.length} available`}</span></div>
            <div className="attempt-actions">
              <button type="button" className="upload-button import-button" aria-expanded={attemptHistoryOpen} aria-controls="attempt-history" onClick={() => setAttemptHistoryOpen((open) => !open)}><History size={15} aria-hidden="true" /> Previous attempts</button>
              <button type="button" className="upload-button" disabled={creatingAttempt} onClick={() => void createAttempt()}><Plus size={16} aria-hidden="true" /> {creatingAttempt ? 'Creating...' : 'New attempt'}</button>
            </div>
            {attemptError && <p className="attempt-error" role="alert">{attemptError}</p>}
            {attemptHistoryOpen && (
              <section id="attempt-history" className="attempt-history" aria-label="Previous attempts">
                {attemptSummariesState === 'loading' && <output>Loading attempts...</output>}
                {attemptSummariesState === 'error' && <p role="alert">{attemptSummariesError}</p>}
                {attemptSummariesState === 'ready' && attemptSummaries.length === 0 && <p>No attempts yet.</p>}
                {attemptSummaries.length > 0 && (
                  <div className="attempt-history-list">
                    {attemptSummaries.map((summary, index) => (
                      <button
                        key={summary.id}
                        type="button"
                        className="attempt-history-item"
                        aria-pressed={selectedAttemptId === summary.id}
                        onClick={() => {
                          if (selectedAttemptId !== summary.id) {
                            setAttemptDetails({ attemptId: summary.id, status: 'loading' })
                          }
                          setSelectedAttemptId(summary.id)
                          setAttemptHistoryOpen(false)
                          setAttemptError('')
                          setAnswerError('')
                          setSelectedClue(null)
                        }}
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
                {attemptDetails?.attemptId === selectedAttempt.id && attemptDetails.status === 'loading' && <span className="attempt-status-note">Loading saved answers...</span>}
                {attemptDetails?.attemptId === selectedAttempt.id && attemptDetails.status === 'error' && (
                  <span className="attempt-status-note" role="alert">
                    {attemptDetails.message}{' '}
                    <button
                      type="button"
                      className="inline-button"
                      onClick={() => {
                        setAttemptDetails({ attemptId: selectedAttempt.id, status: 'loading' })
                        setAttemptReloadKey((key) => key + 1)
                      }}
                    >
                      Retry
                    </button>
                  </span>
                )}
                {loadedAttempt && <span className="attempt-status-note">{savedAnswers.length} saved {savedAnswers.length === 1 ? 'answer' : 'answers'} loaded.</span>}
              </output>
            )}
          </section>
          <div className="puzzle-workspace">
            <section className="puzzle-board-section" aria-labelledby="grid-heading">
              <div className="puzzle-section-heading"><h2 id="grid-heading">Grid</h2><button className="upload-button import-button" type="button" disabled title="Automatic solving is not available yet"><Sparkles size={15} aria-hidden="true" /> Auto-solve</button></div>
              <PuzzleGrid puzzle={state.puzzle} selectedClue={selectedClue} answers={savedAnswers} />
            </section>
            <section className="puzzle-clues-section" aria-label="Puzzle clues">
              {selectedClue && (
                <section className="selected-clue" aria-label="Selected clue">
                  <strong>{selectedClue.id} {selectedClue.direction === 'ACROSS' ? 'Across' : 'Down'}</strong>
                  <p>{selectedClue.text}</p>
                  {selectedSavedAnswer && <p className="saved-answer">Saved answer: <strong>{selectedSavedAnswer.value}</strong></p>}
                  <div className="answer-label"><label htmlFor="clue-answer">Answer</label><span>{answerStatus}</span></div>
                  <div className="answer-entry">
                    <input id="clue-answer" type="text" value={displayedAnswer} onChange={(event) => updateAnswerDraft(event.target.value)} autoComplete="off" autoCapitalize="characters" spellCheck={false} />
                    <div className="answer-actions">
                      <button type="button" className="icon-button" disabled={!hasAnswerDraft || !answerDraft} onClick={() => updateAnswerDraft('')} aria-label="Clear answer draft" title="Clear answer draft"><Eraser size={17} aria-hidden="true" /></button>
                      <button type="button" className="icon-button answer-delete" disabled aria-label="Delete saved answer" title="Saved-answer deletion is not available yet"><Trash2 size={17} aria-hidden="true" /></button>
                      <button type="button" className="icon-button" disabled={!loadedAttempt || !displayedAnswer.trim() || savingAnswer} onClick={() => void submitAnswer()} aria-label={savingAnswer ? 'Submitting answer' : 'Submit answer'} title="Submit answer"><Send size={17} aria-hidden="true" /></button>
                    </div>
                  </div>
                  {!selectedAttemptId && <p className="attempt-status-note">Create or select an attempt before submitting an answer.</p>}
                  {answerError && <p className="attempt-error" role="alert">{answerError}</p>}
                </section>
              )}
              <div className="clue-columns">
                {(['ACROSS', 'DOWN'] as const).map((direction) => (
                  <section key={direction} aria-labelledby={`clues-${direction}`}>
                    <div className="puzzle-section-heading"><h2 id={`clues-${direction}`}>{direction === 'ACROSS' ? <ArrowRight size={16} aria-hidden="true" /> : <ArrowDown size={16} aria-hidden="true" />}{direction === 'ACROSS' ? 'Across' : 'Down'}</h2></div>
                    <ol className="clue-list">
                      {state.puzzle.clues.filter((clue) => clue.direction === direction).sort((first, second) => first.id - second.id).map((clue) => (
                        <li key={`${clue.direction}-${clue.id}`}>
                          <button type="button" className="clue-button" aria-label={`${clue.id} ${direction === 'ACROSS' ? 'Across' : 'Down'}: ${clue.text}`} aria-pressed={selectedClue?.id === clue.id && selectedClue.direction === direction} onClick={() => {
                            setSelectedClue(clue)
                            setAnswerError('')
                          }}>
                            <span className="clue-number">{clue.id}</span>
                            <span>{clue.text}</span>
                            {savedAnswers.find((answer) => answer.id === clueAnswerId(clue)) && (
                              <span className="clue-saved-answer" aria-hidden="true">
                                {savedAnswers.find((answer) => answer.id === clueAnswerId(clue))?.value}
                              </span>
                            )}
                          </button>
                        </li>
                      ))}
                    </ol>
                    {!state.puzzle.clues.some((clue) => clue.direction === direction) && <p className="clue-empty">No {direction.toLowerCase()} clues.</p>}
                  </section>
                ))}
              </div>
            </section>
          </div>
        </>
      )}
    </main>
  )
}

function PuzzleGrid({ puzzle, selectedClue, answers }: Readonly<{ puzzle: Puzzle; selectedClue: PuzzleClue | null; answers: PuzzleAnswer[] }>) {
  const cells = new Map(puzzle.grid.cells.map((cell) => [`${cell.coordinates.x},${cell.coordinates.y}`, cell]))
  const word = selectedClue && puzzle.words.find((entry) => entry.id === selectedClue.id && entry.direction === selectedClue.direction)
  const answerCharacters = new Map<string, string>()
  for (const answer of answers) {
    const clue = puzzle.clues.find((entry) => clueAnswerId(entry) === answer.id)
    const answerWord = clue && puzzle.words.find((entry) => entry.id === clue.id && entry.direction === clue.direction)
    if (!clue || !answerWord) continue

    const characters = answer.value.replace(/\s/g, '').toUpperCase()
    for (let index = 0; index < Math.min(characters.length, answerWord.length); index++) {
      const x = answerWord.coordinates.x + (clue.direction === 'ACROSS' ? index : 0)
      const y = answerWord.coordinates.y - (clue.direction === 'DOWN' ? index : 0)
      answerCharacters.set(`${x},${y}`, characters[index])
    }
  }

  if (puzzle.grid.numberOfRows < 1 || puzzle.grid.numberOfColumns < 1) return <p className="clue-empty">Grid unavailable.</p>

  return (
    <div className="puzzle-grid-scroll">
      <table className="puzzle-grid" aria-label="Puzzle grid">
        <caption className="visually-hidden">{puzzle.name}: {puzzle.grid.numberOfRows} rows, {puzzle.grid.numberOfColumns} columns</caption>
        <tbody>
          {Array.from({ length: puzzle.grid.numberOfRows }, (_, row) => (
            <tr key={row}>
              {Array.from({ length: puzzle.grid.numberOfColumns }, (_, column) => {
                const y = puzzle.grid.numberOfRows - 1 - row
                const cell = cells.get(`${column},${y}`)
                const black = !cell || cell.black
                const character = cell ? answerCharacters.get(`${column},${y}`) ?? cell.character : null
                const highlighted = !black && word && (word.direction === 'ACROSS'
                  ? y === word.coordinates.y && column >= word.coordinates.x && column < word.coordinates.x + word.length
                  : column === word.coordinates.x && y <= word.coordinates.y && y > word.coordinates.y - word.length)
                const cellNumber = cell && cell.id !== null ? `${cell.id}, ` : ''
                const description = black ? 'black square' : cellNumber + (character || 'empty')
                return (
                  <td key={column} className={`${black ? 'puzzle-cell-black' : 'puzzle-cell-white'}${highlighted ? ' puzzle-cell-selected' : ''}`} aria-label={`Row ${row + 1}, column ${column + 1}: ${description}`}>
                    <div className="puzzle-cell-content">
                      {!black && cell.id !== null && <span className="puzzle-cell-number">{cell.id}</span>}
                      {!black && <span className="puzzle-cell-character">{character}</span>}
                    </div>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function clueAnswerId(clue: Pick<PuzzleClue, 'id' | 'direction'>): string {
  return `${clue.id}${clue.direction === 'ACROSS' ? 'A' : 'D'}`
}