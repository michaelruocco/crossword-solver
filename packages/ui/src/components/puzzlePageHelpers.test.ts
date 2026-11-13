import { expect, test } from 'vitest'
import type { Puzzle, PuzzleAttemptSummary } from '../apiClient'
import {
  getAnswerCharacterMap,
  getAnswerLength,
  getAnswerStatus,
  getAttemptLoadError,
  getAttemptLoadStatus,
  getDisplayedAnswerCharacters,
  getLoadedAttempt,
  mergeAttemptSummaries,
  getPuzzleDraftAnswers,
  updateDraftAnswers,
} from './puzzlePageHelpers'

const puzzle: Puzzle = {
  id: 'puzzle-1',
  name: 'Small puzzle',
  createdAt: '2026-10-18T09:30:00Z',
  grid: { numberOfRows: 2, numberOfColumns: 2, cells: [] },
  clues: [
    { id: 1, direction: 'ACROSS', text: 'Across', lengths: [2] },
    { id: 2, direction: 'DOWN', text: 'Down', lengths: [2] },
    { id: 9, direction: 'ACROSS', text: 'No word position', lengths: [1] },
  ],
  words: [
    { id: 1, direction: 'ACROSS', length: 2, coordinates: { x: 0, y: 1 } },
    { id: 2, direction: 'DOWN', length: 2, coordinates: { x: 1, y: 1 } },
  ],
}

const attemptSummary: PuzzleAttemptSummary = {
  id: 'attempt-1',
  createdAt: '2026-10-18T09:30:00Z',
  solving: true,
  answerCount: 0,
  clueCount: 3,
}

test('merges attempt summaries while retaining existing summaries not returned by the request', () => {
  const existing = { ...attemptSummary, id: 'existing', createdAt: '2026-10-17T09:30:00Z' }
  const loaded = { ...attemptSummary, answerCount: 2 }

  expect(mergeAttemptSummaries([existing, { ...loaded, answerCount: 1 }], [loaded])).toEqual([existing, loaded])
})

test('returns null when a ready attempt has no attempt payload', () => {
  expect(getLoadedAttempt({ attemptId: 'attempt-1', status: 'ready' }, 'attempt-1')).toBeNull()
})

test('uses clue lengths when no matching word exists', () => {
  expect(getAnswerLength(puzzle.clues[0], undefined)).toBe(2)
  expect(getAnswerLength(null, puzzle.words[0])).toBe(0)
  expect(getAnswerLength(puzzle.clues[0], puzzle.words[0])).toBe(2)
})

test('returns an empty attempt error message when the error has no message', () => {
  expect(getAttemptLoadError({ attemptId: 'attempt-1', status: 'error' }, 'attempt-1')).toBe('')
})

test('skips answers with no matching word and maps saved and draft letters without overwriting existing cells', () => {
  const characters = getAnswerCharacterMap(
    puzzle,
    [
      { id: '2D', value: 'xy-too-long' },
      { id: '9A', value: 'z' },
      { id: 'unknown', value: 'w' },
    ],
    [{ id: '2D', characters: ['Q', 'R'] }],
    'excluded',
  )

  expect([...characters]).toEqual([['1,1', 'X'], ['1,0', 'Y']])
})

test('includes only populated drafts and fills gaps from matching saved answers', () => {
  expect(getPuzzleDraftAnswers(null, 'attempt-1', {}, [])).toEqual([])
  expect(getPuzzleDraftAnswers(
    puzzle,
    'attempt-1',
    {
      'attempt-1:ACROSS-1': ['', 'b'],
      'attempt-1:DOWN-2': ['', ''],
      'attempt-1:ACROSS-9': ['z'],
    },
    [{ id: '1A', value: 'ac' }],
  )).toEqual([
    { id: '1A', characters: ['A', 'b'] },
    { id: '9A', characters: ['z'] },
  ])
})

test('resolves displayed characters from crossing, draft, saved, and empty values', () => {
  const acrossWord = puzzle.words[0]
  expect(getDisplayedAnswerCharacters(3, acrossWord, new Map([['0,1', 'X']]), ['', 'b'], { id: '1A', value: 'ac' }))
    .toEqual(['X', 'b', ''])
  expect(getDisplayedAnswerCharacters(2, undefined, new Map(), [], undefined)).toEqual(['', ''])
})

test('updates draft characters and removes a draft when its last character is cleared', () => {
  const existing = { '1A': ['A', 'B'] }
  const partiallyCleared = updateDraftAnswers(existing, '1A', 2, 1, '')
  expect(partiallyCleared).toEqual({ '1A': ['A', ''] })
  expect(updateDraftAnswers(partiallyCleared, '1A', 2, 0, '')).toEqual({})
  expect(updateDraftAnswers({}, '1A', 2, 0, '')).toEqual({})
})

test('returns answer status in draft, saved, and empty states', () => {
  expect(getAnswerStatus(true, { id: '1A', value: 'A' })).toBe('Unsaved draft')
  expect(getAnswerStatus(false, { id: '1A', value: 'A' })).toBe('Saved answer')
  expect(getAnswerStatus(false, undefined)).toBe('Not submitted')
})

test('reports selected attempt loading, error, and ready states', () => {
  expect(getAttemptLoadStatus(null, null)).toBeNull()
  expect(getAttemptLoadStatus(attemptSummary, null)).toBe('loading')
  expect(getAttemptLoadStatus(attemptSummary, { attemptId: 'other', status: 'ready' })).toBe('loading')
  expect(getAttemptLoadStatus(attemptSummary, { attemptId: attemptSummary.id, status: 'loading' })).toBe('loading')
  expect(getAttemptLoadStatus(attemptSummary, { attemptId: attemptSummary.id, status: 'error' })).toBe('error')
  expect(getAttemptLoadStatus(attemptSummary, { attemptId: attemptSummary.id, status: 'ready' })).toBeNull()
})
