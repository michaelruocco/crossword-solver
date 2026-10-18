import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { PuzzleUploadDialog } from './PuzzleUploadDialog'

test('uploads a valid image and refreshes after the import completes', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({ id: 'import-1', upload: { url: 'https://bucket.test', fields: { key: 'uploads/puzzle.png' } } }),
        { status: 201, headers: { location: '/v1/puzzles/imports/import-1' } },
      ),
    )
    .mockResolvedValueOnce(new Response(null, { status: 204 }))
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ status: 'COMPLETE', puzzleId: 'puzzle-1' }), { status: 200 }),
    )
  const onClose = vi.fn()
  const onComplete = vi.fn()
  vi.stubGlobal('fetch', fetchMock)

  render(<PuzzleUploadDialog onClose={onClose} onComplete={onComplete} />)
  const file = new File(['puzzle image'], 'puzzle.png', { type: 'image/png' })
  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), { target: { files: [file] } })
  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))

  expect(await screen.findByRole('heading', { name: 'Puzzle imported' })).toBeTruthy()
  expect(fetchMock).toHaveBeenCalledTimes(3)
  expect(onComplete).toHaveBeenCalledOnce()
  expect(onClose).not.toHaveBeenCalled()
})

test('rejects unsupported image types before making an API request', () => {
  const fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  const file = new File(['not an image'], 'puzzle.gif', { type: 'image/gif' })

  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), { target: { files: [file] } })

  expect(screen.getByText('Choose a PNG, JPG, or JPEG file.')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Upload puzzle' }).hasAttribute('disabled')).toBe(true)
  expect(fetchMock).not.toHaveBeenCalled()
})