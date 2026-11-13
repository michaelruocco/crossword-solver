import { useEffect, useRef } from 'react'
import { Eraser, Send, Trash2 } from 'lucide-react'
import type { PuzzleAnswer, PuzzleClue, Puzzle } from '../apiClient'
import { wordCoordinate } from './puzzlePageHelpers'

type Props = Readonly<{
  clue: PuzzleClue
  word: Puzzle['words'][number] | undefined
  savedAnswer: PuzzleAnswer | undefined
  status: string
  characters: string[]
  crossingCharacters: Map<string, string>
  hasDraft: boolean
  attemptSelected: boolean
  saving: boolean
  error: string
  focusKey: string
  canSubmit: boolean
  onChange: (index: number, value: string) => void
  onClear: () => void
  onSubmit: () => void
}>

export function PuzzleAnswerInput({
  clue,
  word,
  savedAnswer,
  status,
  characters,
  crossingCharacters,
  hasDraft,
  attemptSelected,
  saving,
  error,
  focusKey,
  canSubmit,
  onChange,
  onClear,
  onSubmit,
}: Props) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    inputRefs.current.find((input) => input && !input.disabled && !input.value)?.focus()
  }, [focusKey])

  const updateCharacter = (index: number, value: string) => {
    onChange(index, value)
    if (!value) return
    inputRefs.current.slice(index + 1).find((input) => input && !input.disabled)?.focus()
  }

  const handleKeyDown = (index: number, key: string, value: string) => {
    if ((key !== 'Backspace' && key !== 'Delete') || value) return
    inputRefs.current.slice(0, index).reverse()
      .find((input) => input && !input.disabled)?.focus()
  }

  return (
    <section className="selected-clue" aria-label="Selected clue">
      <strong>{clue.id} {clue.direction === 'ACROSS' ? 'Across' : 'Down'}</strong>
      <p>{clue.text}</p>
      {savedAnswer && <p className="saved-answer">Saved answer: <strong>{savedAnswer.value}</strong></p>}
      <div className="answer-label"><span>Answer</span><span>{status}</span></div>
      <div className="answer-entry">
        <fieldset className="answer-character-inputs">
          <legend className="visually-hidden">Answer</legend>
          {characters.map((character, index) => {
            const coordinate = word ? wordCoordinate(word, index) : ''
            const crossingCharacter = crossingCharacters.get(coordinate)
            return (
              <input
                key={coordinate || `${focusKey}:position:${index}`}
                ref={(input) => { inputRefs.current[index] = input }}
                type="text"
                aria-label={`Answer character ${index + 1}`}
                value={character}
                maxLength={1}
                disabled={Boolean(crossingCharacter)}
                onChange={(event) => updateCharacter(index, event.target.value)}
                onKeyDown={(event) => handleKeyDown(index, event.key, character)}
                autoComplete="off"
                autoCapitalize="characters"
                spellCheck={false}
              />
            )
          })}
        </fieldset>
        <div className="answer-actions">
          <button type="button" className="icon-button" disabled={!hasDraft} onClick={onClear} aria-label="Clear answer draft" title="Clear answer draft"><Eraser size={17} aria-hidden="true" /></button>
          <button type="button" className="icon-button answer-delete" disabled aria-label="Delete saved answer" title="Saved-answer deletion is not available yet"><Trash2 size={17} aria-hidden="true" /></button>
          <button type="button" className="icon-button" disabled={!canSubmit || saving} onClick={onSubmit} aria-label={saving ? 'Submitting answer' : 'Submit answer'} title="Submit answer"><Send size={17} aria-hidden="true" /></button>
        </div>
      </div>
      {!attemptSelected && <p className="attempt-status-note">Create or select an attempt before submitting an answer.</p>}
      {error && <p className="attempt-error" role="alert">{error}</p>}
    </section>
  )
}
