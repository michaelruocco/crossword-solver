import { act, fireEvent, render, screen, within } from '@testing-library/react'
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

test('rejects empty and oversized image files', () => {
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  const input = screen.getByLabelText('Choose a puzzle image')

  fireEvent.change(input, { target: { files: [new File([], 'empty.png')] } })
  expect(screen.getByText('The selected file is empty.')).toBeTruthy()

  const oversizedFile = new File(['image'], 'large.png')
  Object.defineProperty(oversizedFile, 'size', { value: 20 * 1024 * 1024 + 1 })
  fireEvent.change(input, { target: { files: [oversizedFile] } })
  expect(screen.getByText('The file must be 20 MB or smaller.')).toBeTruthy()
})

test('does nothing when no file is selected', () => {
  const fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)

  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), { target: { files: [] } })

  expect(screen.getByText('Choose a grid image to add to your library.')).toBeTruthy()
  expect(fetchMock).not.toHaveBeenCalled()
})

test('accepts uppercase extensions and displays file sizes in megabytes', () => {
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  const file = new File([new Uint8Array(1024 * 1024)], 'PUZZLE.PNG', { type: 'image/png' })

  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), { target: { files: [file] } })

  expect(screen.getByText('PUZZLE.PNG')).toBeTruthy()
  expect(screen.getByText('1.0 MB · click to change')).toBeTruthy()
})

test('handles drag state and accepts a dropped image', () => {
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  const dropzone = screen.getByRole('button', { name: 'Choose or drop a puzzle image' })

  fireEvent.dragOver(dropzone)
  expect(dropzone.classList.contains('upload-dropzone-active')).toBe(true)
  fireEvent.dragLeave(dropzone)
  expect(dropzone.classList.contains('upload-dropzone-active')).toBe(false)

  fireEvent.drop(dropzone, {
    dataTransfer: { files: [new File(['image'], 'dropped.png', { type: 'image/png' })] },
  })

  expect(screen.getByText('dropped.png')).toBeTruthy()
})

test('opens the file picker when the dropzone is clicked', () => {
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  const fileInput = screen.getByLabelText('Choose a puzzle image')
  const clickFileInput = vi.spyOn(fileInput, 'click')

  fireEvent.click(screen.getByRole('button', { name: 'Choose or drop a puzzle image' }))

  expect(clickFileInput).toHaveBeenCalledOnce()
})

test('closes from the backdrop when idle', () => {
  const onClose = vi.fn()
  render(<PuzzleUploadDialog onClose={onClose} onComplete={vi.fn()} />)

  fireEvent.click(document.querySelector('.dialog-backdrop-dismiss') as HTMLButtonElement)

  expect(onClose).toHaveBeenCalledOnce()
})

test('does not close from the backdrop while an upload is busy', async () => {
  const onClose = vi.fn()
  const fetchMock = vi.fn((_url: string, options: RequestInit) => new Promise<Response>((_resolve, reject) => {
    options.signal?.addEventListener('abort', () => reject(new Error('Aborted')), { once: true })
  }))
  vi.stubGlobal('fetch', fetchMock)
  render(<PuzzleUploadDialog onClose={onClose} onComplete={vi.fn()} />)
  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), {
    target: { files: [new File(['image'], 'puzzle.png', { type: 'image/png' })] },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))

  fireEvent.click(document.querySelector('.dialog-backdrop-dismiss') as HTMLButtonElement)
  expect(onClose).not.toHaveBeenCalled()

  const dialog = screen.getByRole('dialog', { name: 'Import a puzzle' })
  await act(async () => {
    fireEvent.click(within(dialog).getByRole('button', { name: 'Close upload dialog' }))
    await Promise.resolve()
  })
  expect(onClose).toHaveBeenCalledOnce()
})

test('shows an upload error and offers a retry for a valid file', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Upload service unavailable')))
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), {
    target: { files: [new File(['image'], 'puzzle.png', { type: 'image/png' })] },
  })

  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))

  expect(await screen.findByText('Upload service unavailable')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Try again' }).hasAttribute('disabled')).toBe(false)
})

test('uses a fallback message when an upload fails with a non-Error value', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue('offline'))
  render(<PuzzleUploadDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), {
    target: { files: [new File(['image'], 'puzzle.png', { type: 'image/png' })] },
  })

  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))

  expect(await screen.findByText('Unable to upload this puzzle.')).toBeTruthy()
})

test('does not show an upload error when the upload is aborted on close', async () => {
  const fetchMock = vi.fn((_url: string, options: RequestInit) => new Promise<Response>((_resolve, reject) => {
    options.signal?.addEventListener('abort', () => reject(new Error('Aborted')), { once: true })
  }))
  const onClose = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
  render(<PuzzleUploadDialog onClose={onClose} onComplete={vi.fn()} />)
  fireEvent.change(screen.getByLabelText('Choose a puzzle image'), {
    target: { files: [new File(['image'], 'puzzle.png', { type: 'image/png' })] },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Upload puzzle' }))

  await act(async () => {
    const dialog = screen.getByRole('dialog', { name: 'Import a puzzle' })
    fireEvent.click(within(dialog).getByRole('button', { name: 'Close upload dialog' }))
    await Promise.resolve()
  })

  expect(onClose).toHaveBeenCalledOnce()
  expect(screen.queryByText('Unable to upload this puzzle.')).toBeNull()
})