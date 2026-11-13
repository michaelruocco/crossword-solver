import { fireEvent, render, screen, within } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { expect, test, vi } from 'vitest'
import { PuzzleAttemptSelector } from './PuzzleAttemptSelector'

const summaries = [
  { id: 'attempt-1', createdAt: '2026-10-18T09:30:00Z', solving: false, answerCount: 3, clueCount: 3 },
  { id: 'attempt-2', createdAt: '2026-10-19T09:30:00Z', solving: true, answerCount: 1, clueCount: 3 },
]

function renderSelector(overrides: Partial<ComponentProps<typeof PuzzleAttemptSelector>> = {}) {
  const props: ComponentProps<typeof PuzzleAttemptSelector> = {
    summaries,
    summariesState: 'ready',
    summariesError: '',
    selectedAttemptId: summaries[1].id,
    historyOpen: true,
    creatingAttempt: false,
    attemptError: '',
    attemptLoadStatus: null,
    attemptLoadError: '',
    selectedAttempt: summaries[1],
    selectedAttemptNumber: 2,
    savedAnswerCount: 1,
    onToggleHistory: vi.fn(),
    onCreateAttempt: vi.fn(),
    onSelectAttempt: vi.fn(),
    onRetryAttempt: vi.fn(),
    ...overrides,
  }
  const result = render(<PuzzleAttemptSelector {...props} />)
  return { props, ...result }
}

test('displays numbered attempts and reports selection, history, and creation actions', () => {
  const { props } = renderSelector()

  expect(screen.getByText('Selected attempt 2')).toBeTruthy()
  expect(screen.getByRole('button', { name: /Attempt 1/ }).getAttribute('aria-pressed')).toBe('false')
  expect(screen.getByRole('button', { name: /Attempt 2/ }).getAttribute('aria-pressed')).toBe('true')

  fireEvent.click(screen.getByRole('button', { name: /Attempt 1/ }))
  fireEvent.click(screen.getByRole('button', { name: 'Previous attempts' }))
  fireEvent.click(screen.getByRole('button', { name: 'New attempt' }))

  expect(props.onSelectAttempt).toHaveBeenCalledWith('attempt-1')
  expect(props.onToggleHistory).toHaveBeenCalledOnce()
  expect(props.onCreateAttempt).toHaveBeenCalledOnce()
})

test('displays loading, error, empty-history, and selected-attempt retry states', () => {
  const { props, rerender } = renderSelector({
    summariesState: 'loading',
    selectedAttemptNumber: 2,
    attemptLoadStatus: 'error',
    attemptLoadError: 'Attempt unavailable',
  })

  expect(screen.getByText('Loading attempts...')).toBeTruthy()
  expect(screen.getByText('Selected attempt 2')).toBeTruthy()
  const status = screen.getByRole('status', { name: 'Selected attempt status' })
  expect(within(status).getByText('Attempt unavailable')).toBeTruthy()
  fireEvent.click(within(status).getByRole('button', { name: 'Retry' }))
  expect(props.onRetryAttempt).toHaveBeenCalledWith('attempt-2')

  rerender(<PuzzleAttemptSelector
    {...props}
    summariesState="error"
    summariesError="History unavailable"
    selectedAttempt={null}
    selectedAttemptId={null}
    selectedAttemptNumber={null}
    attemptLoadStatus={null}
  />)
  expect(screen.getByText('History unavailable')).toBeTruthy()

  rerender(<PuzzleAttemptSelector
    {...props}
    summaries={[]}
    summariesState="ready"
    selectedAttempt={null}
    selectedAttemptId={null}
    selectedAttemptNumber={null}
    attemptLoadStatus={null}
  />)
  expect(screen.getByText('No attempts yet.')).toBeTruthy()
})
