import { useEffect, useRef, useState, type SubmitEvent } from 'react'
import { Check, Link2, LoaderCircle, X } from 'lucide-react'
import { apiClient } from '../apiClient'

interface PuzzleImportDialogProps {
  onClose: () => void
  onComplete: () => void
}

type ImportStage = 'select' | 'requesting' | 'processing' | 'complete' | 'error'

function isImageUrl(value: string): boolean {
  try {
    const url = new URL(value)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

export function PuzzleImportDialog({ onClose, onComplete }: Readonly<PuzzleImportDialogProps>) {
  const [imageUrl, setImageUrl] = useState('')
  const [stage, setStage] = useState<ImportStage>('select')
  const [errorMessage, setErrorMessage] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const isBusy = stage === 'requesting' || stage === 'processing'

  useEffect(() => {
    inputRef.current?.focus()
    return () => abortControllerRef.current?.abort()
  }, [])

  const close = () => {
    abortControllerRef.current?.abort()
    onClose()
  }

  const importPuzzle = async (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (isBusy) return
    const trimmedUrl = imageUrl.trim()
    if (!isImageUrl(trimmedUrl)) {
      setErrorMessage('Enter a valid HTTP or HTTPS image URL.')
      setStage('error')
      inputRef.current?.focus()
      return
    }

    const controller = new AbortController()
    abortControllerRef.current = controller
    setErrorMessage('')
    setStage('requesting')
    try {
      const request = await apiClient.startPuzzleImport(trimmedUrl, controller.signal)
      if (controller.signal.aborted) return
      setStage('processing')
      await apiClient.waitForPuzzleImport(request.location, controller.signal)
      if (controller.signal.aborted) return
      setStage('complete')
      onComplete()
    } catch (error) {
      if (controller.signal.aborted) return
      setErrorMessage(error instanceof Error ? error.message : 'Unable to import this puzzle.')
      setStage('error')
    } finally {
      abortControllerRef.current = null
    }
  }

  const statusMessage = {
    select: '',
    requesting: 'Starting puzzle import...',
    processing: 'Preparing your puzzle...',
    complete: 'Your puzzle is ready in the library.',
    error: errorMessage,
  }[stage]

  let primaryLabel = 'Import puzzle'
  if (isBusy) primaryLabel = 'Working...'
  else if (stage === 'error') primaryLabel = 'Try again'

  return (
    <div className="dialog-backdrop">
      <button
        className="dialog-backdrop-dismiss"
        type="button"
        tabIndex={-1}
        aria-label="Close import dialog"
        onClick={() => {
          if (!isBusy) close()
        }}
      />
      <dialog
        className="upload-dialog"
        open
        aria-modal="true"
        aria-labelledby="import-title"
        onKeyDown={(event) => {
          if (event.key === 'Escape') close()
        }}
      >
        <header className="dialog-header">
          <div className="dialog-heading-icon"><Link2 size={18} aria-hidden="true" /></div>
          <div>
            <h2 id="import-title">Import from URL</h2>
          </div>
          <button className="dialog-close" type="button" onClick={close} aria-label="Close import dialog">
            <X size={19} aria-hidden="true" />
          </button>
        </header>

        {stage === 'complete' ? (
          <output className="upload-complete">
            <span className="complete-mark"><Check size={25} aria-hidden="true" /></span>
            <h3>Puzzle imported</h3>
            <p>{statusMessage}</p>
            <button className="upload-primary" type="button" onClick={close}>Done</button>
          </output>
        ) : (
          <form onSubmit={importPuzzle} noValidate>
            <div className="import-url-field">
              <label htmlFor="puzzle-image-url">Image URL</label>
              <input
                ref={inputRef}
                id="puzzle-image-url"
                type="url"
                inputMode="url"
                autoComplete="url"
                placeholder="https://example.com/puzzle.png"
                value={imageUrl}
                disabled={isBusy}
                aria-invalid={stage === 'error'}
                aria-describedby="import-status"
                onChange={(event) => {
                  setImageUrl(event.currentTarget.value)
                  setStage('select')
                  setErrorMessage('')
                }}
              />
            </div>
            <div id="import-status" className={`upload-status ${stage === 'error' ? 'upload-status-error' : ''}`} aria-live="polite">
              {isBusy && <LoaderCircle size={15} className="spin" aria-hidden="true" />}
              {stage === 'error' && <X size={15} aria-hidden="true" />}
              {statusMessage}
            </div>
            <div className="upload-actions">
              <button className="upload-cancel" type="button" onClick={close} disabled={isBusy}>Cancel</button>
              <button className="upload-primary" type="submit" disabled={!imageUrl.trim() || isBusy}>
                {primaryLabel}
              </button>
            </div>
          </form>
        )}
      </dialog>
    </div>
  )
}