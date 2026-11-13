import type { Puzzle, PuzzleAnswer, PuzzleAttemptSummary, PuzzleClue } from '../apiClient'

export type PuzzleDraftAnswer = { id: string; characters: string[] }
export type AttemptLoadStatus = 'loading' | 'error' | null

export function clueAnswerId(clue: Pick<PuzzleClue, 'id' | 'direction'>): string {
  return `${clue.id}${clue.direction === 'ACROSS' ? 'A' : 'D'}`
}

export function normalizeAnswer(value: string): string[] {
  return Array.from(value.replace(/\s/g, '').toUpperCase())
}

export function wordCoordinate(word: Puzzle['words'][number], index: number): string {
  const x = word.coordinates.x + (word.direction === 'ACROSS' ? index : 0)
  const y = word.coordinates.y - (word.direction === 'DOWN' ? index : 0)
  return `${x},${y}`
}

export function getAnswerCharacterMap(
  puzzle: Puzzle,
  answers: PuzzleAnswer[],
  drafts: PuzzleDraftAnswer[],
  excludedAnswerId: string,
): Map<string, string> {
  const characters = new Map<string, string>()
  const answerValues = [
    ...answers.filter((answer) => answer.id !== excludedAnswerId)
      .map((answer) => ({ id: answer.id, characters: normalizeAnswer(answer.value) })),
    ...drafts.filter((draft) => draft.id !== excludedAnswerId),
  ]
  for (const answer of answerValues) {
    const clue = puzzle.clues.find((entry) => clueAnswerId(entry) === answer.id)
    const word = clue && puzzle.words.find((entry) => entry.id === clue.id && entry.direction === clue.direction)
    if (!word) continue
    for (let index = 0; index < Math.min(answer.characters.length, word.length); index++) {
      const character = answer.characters[index]
      const coordinate = wordCoordinate(word, index)
      if (character && !characters.has(coordinate)) characters.set(coordinate, character)
    }
  }
  return characters
}

export function getPuzzleDraftAnswers(
  puzzle: Puzzle | null,
  selectedAttemptId: string | null,
  answerDrafts: Record<string, string[]>,
  savedAnswers: PuzzleAnswer[],
): PuzzleDraftAnswer[] {
  if (!puzzle) return []
  return puzzle.clues.flatMap((clue) => {
    const key = `${selectedAttemptId ?? 'unselected'}:${clue.direction}-${clue.id}`
    const characters = answerDrafts[key]
    if (!characters?.some(Boolean)) return []
    const savedCharacters = normalizeAnswer(
      savedAnswers.find((answer) => answer.id === clueAnswerId(clue))?.value ?? '',
    )
    return [{
      id: clueAnswerId(clue),
      characters: characters.map((character, index) => character || savedCharacters[index] || ''),
    }]
  })
}

export function getDisplayedAnswerCharacters(
  length: number,
  word: Puzzle['words'][number] | undefined,
  crossingCharacters: Map<string, string>,
  draftCharacters: string[],
  savedAnswer: PuzzleAnswer | undefined,
): string[] {
  const savedCharacters = savedAnswer ? normalizeAnswer(savedAnswer.value) : []
  return Array.from({ length }, (_, index) => {
    const coordinate = word ? wordCoordinate(word, index) : ''
    return crossingCharacters.get(coordinate) ?? draftCharacters[index] ?? savedCharacters[index] ?? ''
  })
}

export function updateDraftAnswers(
  drafts: Record<string, string[]>,
  key: string,
  length: number,
  index: number,
  value: string,
): Record<string, string[]> {
  const updatedAnswer = Array.from({ length }, (_, characterIndex) => drafts[key]?.[characterIndex] ?? '')
  updatedAnswer[index] = Array.from(value.toUpperCase())[0] ?? ''
  if (updatedAnswer.some(Boolean)) return { ...drafts, [key]: updatedAnswer }
  const updatedDrafts = { ...drafts }
  delete updatedDrafts[key]
  return updatedDrafts
}

export function getAnswerStatus(hasDraft: boolean, savedAnswer: PuzzleAnswer | undefined): string {
  if (hasDraft) return 'Unsaved draft'
  if (savedAnswer) return 'Saved answer'
  return 'Not submitted'
}

export function getAttemptLoadStatus(
  selectedAttempt: PuzzleAttemptSummary | null,
  attemptDetails: { attemptId: string; status: string } | null,
): AttemptLoadStatus {
  if (!selectedAttempt) return null
  if (attemptDetails?.attemptId !== selectedAttempt.id) return 'loading'
  if (attemptDetails.status === 'ready') return null
  return attemptDetails.status === 'error' ? 'error' : 'loading'
}
