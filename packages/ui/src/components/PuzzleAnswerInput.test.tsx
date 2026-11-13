import { fireEvent, render, screen } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { expect, test, vi } from 'vitest'
import type { PuzzleClue } from '../apiClient'
import { PuzzleAnswerInput } from './PuzzleAnswerInput'

const clue: PuzzleClue = { id: 1, direction: 'ACROSS', text: 'A clue', lengths: [3] }
const word = { id: 1, direction: 'ACROSS' as const, length: 3, coordinates: { x: 0, y: 1 } }

function renderAnswerInput(overrides: Partial<ComponentProps<typeof PuzzleAnswerInput>> = {}) {
  const props: ComponentProps<typeof PuzzleAnswerInput> = {
    clue,
    word,
    savedAnswer: undefined,
    status: 'Not submitted',
    characters: ['', '', ''],
    crossingCharacters: new Map(),
    hasDraft: false,
    attemptSelected: true,
    saving: false,
    error: '',
    focusKey: 'attempt-1:ACROSS-1',
    canSubmit: false,
    onChange: vi.fn(),
    onClear: vi.fn(),
    onSubmit: vi.fn(),
    ...overrides,
  }
  render(<PuzzleAnswerInput {...props} />)
  return props
}

function input(index: number): HTMLInputElement {
  return screen.getByRole('textbox', { name: `Answer character ${index}` }) as HTMLInputElement
}

test('focuses the first empty editable input and advances over locked crossing letters', () => {
  renderAnswerInput({
    characters: ['A', '', ''],
    crossingCharacters: new Map([['1,1', 'B']]),
  })

  expect(document.activeElement).toBe(input(3))
  expect(input(2).disabled).toBe(true)
  fireEvent.change(input(1), { target: { value: 'x' } })
  expect(document.activeElement).toBe(input(3))
})

test('renders editable answer positions when the clue has no grid word', () => {
  const onChange = vi.fn()
  renderAnswerInput({ word: undefined, onChange })

  expect(input(1).disabled).toBe(false)
  fireEvent.change(input(1), { target: { value: 'c' } })

  expect(onChange).toHaveBeenCalledWith(0, 'c')
})

test('moves backward from an empty input to the previous editable input', () => {
  renderAnswerInput({ crossingCharacters: new Map([['1,1', 'B']]) })
  input(3).focus()

  fireEvent.keyDown(input(3), { key: 'Backspace', code: 'Backspace' })
  expect(document.activeElement).toBe(input(1))

  input(3).focus()
  fireEvent.keyDown(input(3), { key: 'Delete', code: 'Delete' })
  expect(document.activeElement).toBe(input(1))
})

test('keeps focus for other keys and populated input deletion, and reports answer actions', () => {
  const onChange = vi.fn()
  const onClear = vi.fn()
  const onSubmit = vi.fn()
  renderAnswerInput({
    characters: ['A', 'B', 'C'],
    hasDraft: true,
    attemptSelected: false,
    saving: true,
    error: 'Answer rejected',
    canSubmit: true,
    onChange,
    onClear,
    onSubmit,
  })

  input(2).focus()
  fireEvent.keyDown(input(2), { key: 'ArrowLeft', code: 'ArrowLeft' })
  fireEvent.keyDown(input(2), { key: 'Backspace', code: 'Backspace' })
  expect(document.activeElement).toBe(input(2))
  expect(screen.getByText('Create or select an attempt before submitting an answer.')).toBeTruthy()
  expect(screen.getByRole('alert').textContent).toBe('Answer rejected')
  fireEvent.click(screen.getByRole('button', { name: 'Clear answer draft' }))
  fireEvent.click(screen.getByRole('button', { name: 'Submitting answer' }))
  expect(onClear).toHaveBeenCalledOnce()
  expect(onSubmit).not.toHaveBeenCalled()
  fireEvent.change(input(1), { target: { value: 'x' } })
  expect(onChange).toHaveBeenCalledWith(0, 'x')
})
