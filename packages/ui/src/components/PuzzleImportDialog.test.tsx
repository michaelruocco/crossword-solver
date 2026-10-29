import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { PuzzleImportDialog } from './PuzzleImportDialog'

function enterUrl(value = 'https://images.test/puzzle.png') {
  fireEvent.change(screen.getByRole('textbox', { name: 'Image URL' }), { target: { value } })
}

function submit() {
  fireEvent.click(screen.getByRole('button', { name: /Import puzzle|Try again/ }))
}

test.each(['https://images.test/puzzle.png', 'http://images.test/puzzle.webp?download=1'])(
  'imports %s and notifies the library only after completion', async (imageUrl) => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: 'import-1' }), {
        status: 202,
        headers: { location: '/v1/puzzles/imports/import-1' },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'COMPLETE', puzzleId: 'puzzle-1' })))
    vi.stubGlobal('fetch', fetchMock)
    const onComplete = vi.fn()
    const onClose = vi.fn()
    render(<PuzzleImportDialog onClose={onClose} onComplete={onComplete} />)

    expect(document.activeElement).toBe(screen.getByRole('textbox', { name: 'Image URL' }))
    expect(screen.getByRole('button', { name: 'Import puzzle' }).hasAttribute('disabled')).toBe(true)
    enterUrl(`  ${imageUrl}  `)
    submit()
    expect(onComplete).not.toHaveBeenCalled()

    expect(await screen.findByRole('heading', { name: 'Puzzle imported' })).toBeTruthy()
    expect(JSON.parse(fetchMock.mock.calls[0][1].body as string)).toEqual({ imageUrl })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(onComplete).toHaveBeenCalledOnce()
    expect(onClose).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Done' }))
    expect(onClose).toHaveBeenCalledOnce()
  },
)

test.each(['not a url', 'file:///etc/passwd', 'ftp://images.test/puzzle.png', '/puzzle.png'])(
  'rejects invalid URL %s before making a request', (imageUrl) => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    render(<PuzzleImportDialog onClose={vi.fn()} onComplete={vi.fn()} />)
    enterUrl(imageUrl)
    submit()

    expect(screen.getByText('Enter a valid HTTP or HTTPS image URL.')).toBeTruthy()
    expect(screen.getByRole('textbox', { name: 'Image URL' }).getAttribute('aria-invalid')).toBe('true')
    expect(fetchMock).not.toHaveBeenCalled()
    enterUrl()
    expect(screen.queryByText('Enter a valid HTTP or HTTPS image URL.')).toBeNull()
  },
)

test('disables submission for whitespace-only input', () => {
  render(<PuzzleImportDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  enterUrl('   ')
  expect(screen.getByRole('button', { name: 'Import puzzle' }).hasAttribute('disabled')).toBe(true)
})

test('reports backend errors and retries the same URL successfully', async () => {
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ message: 'Image unavailable' }), { status: 400 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ id: 'import-1' }), { status: 202 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'COMPLETE' }))))
  const onComplete = vi.fn()
  render(<PuzzleImportDialog onClose={vi.fn()} onComplete={onComplete} />)
  enterUrl()
  submit()

  expect(await screen.findByText('Image unavailable')).toBeTruthy()
  expect(onComplete).not.toHaveBeenCalled()
  submit()
  expect(await screen.findByRole('heading', { name: 'Puzzle imported' })).toBeTruthy()
  expect(onComplete).toHaveBeenCalledOnce()
})

test('reports a processing failure without refreshing the library', async () => {
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ id: 'import-1' }), { status: 202 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'FAILED', error: 'No grid found' }))))
  const onComplete = vi.fn()
  render(<PuzzleImportDialog onClose={vi.fn()} onComplete={onComplete} />)
  enterUrl()
  submit()

  expect(await screen.findByText('No grid found')).toBeTruthy()
  expect(onComplete).not.toHaveBeenCalled()
})

test('reports a fallback error for non-Error failures', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue('offline'))
  render(<PuzzleImportDialog onClose={vi.fn()} onComplete={vi.fn()} />)
  enterUrl()
  submit()
  expect(await screen.findByText('Unable to import this puzzle.')).toBeTruthy()
})

test.each(['Cancel', 'backdrop', 'Escape'])('closes the idle dialog using %s', (action) => {
  const onClose = vi.fn()
  render(<PuzzleImportDialog onClose={onClose} onComplete={vi.fn()} />)
  if (action === 'backdrop') {
    fireEvent.click(document.querySelector('.dialog-backdrop-dismiss') as HTMLButtonElement)
  } else if (action === 'Escape') {
    fireEvent.keyDown(screen.getByRole('textbox', { name: 'Image URL' }), { key: 'Escape' })
  } else {
    fireEvent.click(screen.getByRole('button', { name: action }))
  }
  expect(onClose).toHaveBeenCalledOnce()
})

test('does not close the dialog for keys other than Escape', () => {
  const onClose = vi.fn()
  render(<PuzzleImportDialog onClose={onClose} onComplete={vi.fn()} />)

  fireEvent.keyDown(screen.getByRole('textbox', { name: 'Image URL' }), { key: 'Tab' })

  expect(onClose).not.toHaveBeenCalled()
})

test.each(['requesting', 'processing'])(
  'ignores duplicate submissions and a late successful response while %s after close', async (stage) => {
    let resolveResponse: (response: Response) => void = () => undefined
    const pendingResponse = new Promise<Response>((resolve) => { resolveResponse = resolve })
    const fetchMock = vi.fn()
    if (stage === 'processing') {
      fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ id: 'import-1' }), { status: 202 }))
    }
    fetchMock.mockReturnValueOnce(pendingResponse)
    vi.stubGlobal('fetch', fetchMock)
    const onClose = vi.fn()
    const onComplete = vi.fn()
    render(<PuzzleImportDialog onClose={onClose} onComplete={onComplete} />)
    enterUrl()
    submit()

    const statusMessage = stage === 'requesting' ? 'Starting puzzle import...' : 'Preparing your puzzle...'
    expect(await screen.findByText(statusMessage)).toBeTruthy()
    const expectedRequests = stage === 'requesting' ? 1 : 2
    const input = screen.getByRole('textbox', { name: 'Image URL' })
    fireEvent.submit(input.closest('form') as HTMLFormElement)
    expect(fetchMock).toHaveBeenCalledTimes(expectedRequests)

    await act(async () => {
      const dialog = screen.getByRole('dialog', { name: 'Import from URL' })
      fireEvent.click(within(dialog).getByRole('button', { name: 'Close import dialog' }))
      resolveResponse(new Response(JSON.stringify(
        stage === 'requesting' ? { id: 'import-1' } : { status: 'COMPLETE', puzzleId: 'puzzle-1' },
      )))
    })

    expect(fetchMock.mock.calls[expectedRequests - 1][1].signal.aborted).toBe(true)
    expect(fetchMock).toHaveBeenCalledTimes(expectedRequests)
    expect(onClose).toHaveBeenCalledOnce()
    expect(onComplete).not.toHaveBeenCalled()
    expect(screen.queryByRole('heading', { name: 'Puzzle imported' })).toBeNull()
    expect(screen.queryByText('Unable to import this puzzle.')).toBeNull()
  },
)

test.each(['close', 'unmount'])('aborts an in-flight request on %s without reporting an error', async (action) => {
  const fetchMock = vi.fn((_url: string, options: RequestInit) => new Promise<Response>((_resolve, reject) => {
    options.signal?.addEventListener('abort', () => reject(new Error('Aborted')), { once: true })
  }))
  vi.stubGlobal('fetch', fetchMock)
  const onClose = vi.fn()
  const onComplete = vi.fn()
  const { unmount } = render(<PuzzleImportDialog onClose={onClose} onComplete={onComplete} />)
  enterUrl()
  submit()

  expect(screen.getByRole('textbox', { name: 'Image URL' }).hasAttribute('disabled')).toBe(true)
  expect(screen.getByRole('button', { name: 'Working...' }).hasAttribute('disabled')).toBe(true)
  fireEvent.click(document.querySelector('.dialog-backdrop-dismiss') as HTMLButtonElement)
  expect(onClose).not.toHaveBeenCalled()

  await act(async () => {
    if (action === 'unmount') unmount()
    else {
      const dialog = screen.getByRole('dialog', { name: 'Import from URL' })
      fireEvent.click(within(dialog).getByRole('button', { name: 'Close import dialog' }))
    }
  })

  expect(fetchMock.mock.calls[0][1].signal?.aborted).toBe(true)
  expect(screen.queryByText('Aborted')).toBeNull()
  expect(onComplete).not.toHaveBeenCalled()
})