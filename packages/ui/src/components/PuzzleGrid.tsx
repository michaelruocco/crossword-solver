import type { Puzzle, PuzzleAnswer, PuzzleClue } from '../apiClient'
import { clueAnswerId, normalizeAnswer, type PuzzleDraftAnswer, wordCoordinate } from './puzzlePageHelpers'

export function PuzzleGrid({ puzzle, selectedClue, answers, drafts }: Readonly<{
  puzzle: Puzzle
  selectedClue: PuzzleClue | null
  answers: PuzzleAnswer[]
  drafts: PuzzleDraftAnswer[]
}>) {
  const cells = new Map(puzzle.grid.cells.map((cell) => [`${cell.coordinates.x},${cell.coordinates.y}`, cell]))
  const word = selectedClue && puzzle.words.find((entry) => entry.id === selectedClue.id && entry.direction === selectedClue.direction)
  const answerCharacters = new Map<string, string>()
  const answersToMap = answers.map((answer) => ({ id: answer.id, characters: normalizeAnswer(answer.value) }))
  for (const answer of [...answersToMap, ...drafts]) {
    const clue = puzzle.clues.find((entry) => clueAnswerId(entry) === answer.id)
    const answerWord = clue && puzzle.words.find((entry) => entry.id === clue.id && entry.direction === clue.direction)
    if (!clue || !answerWord) continue

    for (let index = 0; index < Math.min(answer.characters.length, answerWord.length); index++) {
      const character = answer.characters[index]
      if (!character) continue
      const coordinate = wordCoordinate(answerWord, index)
      if (!answerCharacters.has(coordinate)) answerCharacters.set(coordinate, character)
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
