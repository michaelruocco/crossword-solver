import { ArrowDown, ArrowRight } from 'lucide-react'
import type { PuzzleAnswer, PuzzleClue } from '../apiClient'
import { clueAnswerId } from './puzzlePageHelpers'

type Props = Readonly<{
  clues: PuzzleClue[]
  savedAnswers: PuzzleAnswer[]
  selectedClue: PuzzleClue | null
  onSelect: (clue: PuzzleClue) => void
}>

export function PuzzleClueList({ clues, savedAnswers, selectedClue, onSelect }: Props) {
  return (
    <div className="clue-columns">
      {(['ACROSS', 'DOWN'] as const).map((direction) => {
        const directionClues = clues.filter((clue) => clue.direction === direction)
          .sort((first, second) => first.id - second.id)
        const DirectionIcon = direction === 'ACROSS' ? ArrowRight : ArrowDown
        const directionLabel = direction === 'ACROSS' ? 'Across' : 'Down'
        return (
          <section key={direction} aria-labelledby={`clues-${direction}`}>
            <div className="puzzle-section-heading"><h2 id={`clues-${direction}`}><DirectionIcon size={16} aria-hidden="true" />{directionLabel}</h2></div>
            <ol className="clue-list">
              {directionClues.map((clue) => {
                const savedAnswer = savedAnswers.find((answer) => answer.id === clueAnswerId(clue))
                return (
                  <li key={`${clue.direction}-${clue.id}`}>
                    <button
                      type="button"
                      className="clue-button"
                      aria-label={`${clue.id} ${directionLabel}: ${clue.text}`}
                      aria-pressed={selectedClue?.id === clue.id && selectedClue.direction === direction}
                      onClick={() => onSelect(clue)}
                    >
                      <span className="clue-number">{clue.id}</span>
                      <span>{clue.text}</span>
                      {savedAnswer && <span className="clue-saved-answer" aria-hidden="true">{savedAnswer.value}</span>}
                    </button>
                  </li>
                )
              })}
            </ol>
            {directionClues.length === 0 && <p className="clue-empty">No {direction.toLowerCase()} clues.</p>}
          </section>
        )
      })}
    </div>
  )
}
