import type { Puzzle, PuzzleAnswer, PuzzleAttempt, PuzzleAttemptSummary, PuzzleClue } from '../apiClient'

export type PuzzleDraftAnswer = { id: string; characters: string[] }
export type AttemptLoadStatus = 'loading' | 'error' | null
type PuzzlePageState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; puzzle: Puzzle }

export function sortAttemptsNewestFirst(summaries: PuzzleAttemptSummary[]): PuzzleAttemptSummary[] {
  return [...summaries].sort((first, second) => Date.parse(second.createdAt) - Date.parse(first.createdAt))
}

export function mergeAttemptSummaries(
  existing: PuzzleAttemptSummary[],
  loaded: PuzzleAttemptSummary[],
): PuzzleAttemptSummary[] {
  const loadedIds = new Set(loaded.map((summary) => summary.id))
  return sortAttemptsNewestFirst([
    ...loaded,
    ...existing.filter((summary) => !loadedIds.has(summary.id)),
  ])
}

export function clueAnswerId(clue: Pick<PuzzleClue, 'id' | 'direction'>): string {
  return `${clue.id}${clue.direction === 'ACROSS' ? 'A' : 'D'}`
}

export function getPuzzleFromState(state: PuzzlePageState): Puzzle | null {
  return state.status === 'ready' ? state.puzzle : null
}

export function getSelectedAttempt(
  summaries: PuzzleAttemptSummary[],
  selectedAttemptId: string | null,
): PuzzleAttemptSummary | null {
  return summaries.find((summary) => summary.id === selectedAttemptId) ?? null
}

export function getSelectedAttemptNumber(
  summaries: PuzzleAttemptSummary[],
  selectedAttempt: PuzzleAttemptSummary | null,
): number | null {
  return selectedAttempt ? summaries.findIndex((summary) => summary.id === selectedAttempt.id) + 1 : null
}

export function getLoadedAttempt(
  attemptDetails: { attemptId: string; status: string; attempt?: PuzzleAttempt } | null,
  selectedAttemptId: string | null,
): PuzzleAttempt | null {
  return attemptDetails?.status === 'ready' && attemptDetails.attemptId === selectedAttemptId
    ? attemptDetails.attempt ?? null
    : null
}

export function getSelectedSavedAnswer(
  clue: PuzzleClue | null,
  savedAnswers: PuzzleAnswer[],
): PuzzleAnswer | undefined {
  return clue ? savedAnswers.find((answer) => answer.id === clueAnswerId(clue)) : undefined
}

export function getSelectedWord(
  puzzle: Puzzle | null,
  clue: PuzzleClue | null,
): Puzzle['words'][number] | undefined {
  return puzzle && clue
    ? puzzle.words.find((word) => word.id === clue.id && word.direction === clue.direction)
    : undefined
}

export function getAnswerLength(clue: PuzzleClue | null, word: Puzzle['words'][number] | undefined): number {
  return clue ? word?.length ?? clue.lengths.reduce((length, part) => length + part, 0) : 0
}

export function getSelectedCrossingCharacters(
  puzzle: Puzzle | null,
  clue: PuzzleClue | null,
  savedAnswers: PuzzleAnswer[],
  draftAnswers: PuzzleDraftAnswer[],
): Map<string, string> {
  return puzzle && clue
    ? getAnswerCharacterMap(puzzle, savedAnswers, draftAnswers, clueAnswerId(clue))
    : new Map<string, string>()
}

export function getAttemptLoadError(
  attemptDetails: { attemptId: string; status: string; message?: string } | null,
  selectedAttemptId: string | null,
): string {
  return attemptDetails?.status === 'error' && attemptDetails.attemptId === selectedAttemptId
    ? attemptDetails.message ?? ''
    : ''
}

export function canSubmitAnswer(submitAvailable: boolean, characters: string[]): boolean {
  return submitAvailable && characters.length > 0 && characters.every(Boolean)
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
