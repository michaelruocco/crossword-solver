import { useEffect, useRef, useState, type ChangeEvent, type DragEvent, type KeyboardEvent } from 'react'
import { Check, FileImage, LoaderCircle, Upload, X } from 'lucide-react'
import { apiClient } from '../apiClient'

interface PuzzleUploadDialogProps {
  onClose: () => void
  onComplete: () => void
}

type UploadStage = 'select' | 'requesting' | 'uploading' | 'processing' | 'complete' | 'error'

const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
const ALLOWED_EXTENSIONS = new Set(['png', 'jpg', 'jpeg'])

function validateFile(file: File): string | null {
  const extension = file.name.split('.').pop()?.toLocaleLowerCase() ?? ''
  if (!ALLOWED_EXTENSIONS.has(extension)) return 'Choose a PNG, JPG, or JPEG file.'
  if (file.size === 0) return 'The selected file is empty.'
  if (file.size > MAX_FILE_SIZE_BYTES) return 'The file must be 20 MB or smaller.'
  return null
}

function formatFileSize(size: number): string {
  return size >= 1024 * 1024 ? `${(size / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(size / 1024))} KB`
}

export function PuzzleUploadDialog({ onClose, onComplete }: PuzzleUploadDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const [stage, setStage] = useState<UploadStage>('select')
  const [errorMessage, setErrorMessage] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const isBusy = stage === 'requesting' || stage === 'uploading' || stage === 'processing'

  useEffect(() => () => abortControllerRef.current?.abort(), [])

  const close = () => {
    abortControllerRef.current?.abort()
    onClose()
  }

  const chooseFile = (candidate: File | undefined) => {
    if (!candidate) return
    const validationError = validateFile(candidate)
    setErrorMessage(validationError ?? '')
    setFile(validationError ? null : candidate)
    setStage(validationError ? 'error' : 'select')
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => chooseFile(event.currentTarget.files?.[0])

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    chooseFile(event.dataTransfer.files[0])
  }

  const handleDropKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      fileInputRef.current?.click()
    }
  }

  const upload = async () => {
    if (!file) return
    const controller = new AbortController()
    abortControllerRef.current = controller
    setErrorMessage('')

    try {
      setStage('requesting')
      const uploadRequest = await apiClient.startPuzzleUpload(file.name, controller.signal)
      setStage('uploading')
      await apiClient.uploadPuzzleFile(uploadRequest.upload, file, controller.signal)
      setStage('processing')
      await apiClient.waitForPuzzleImport(uploadRequest.location, controller.signal)
      setStage('complete')
      onComplete()
    } catch (error) {
      if (controller.signal.aborted) return
      setErrorMessage(error instanceof Error ? error.message : 'Unable to upload this puzzle.')
      setStage('error')
    } finally {
      abortControllerRef.current = null
    }
  }

  const statusMessage = {
    select: 'Choose a grid image to add to your library.',
    requesting: 'Preparing a secure upload…',
    uploading: 'Uploading your image directly to storage…',
    processing: 'Image uploaded. Preparing your puzzle…',
    complete: 'Your puzzle is ready in the library.',
    error: errorMessage,
  }[stage]

  return (
    <div
      className="dialog-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isBusy) close()
      }}
    >
      <section className="upload-dialog" role="dialog" aria-modal="true" aria-labelledby="upload-title">
        <header className="dialog-header">
          <div className="dialog-heading-icon"><Upload size={18} aria-hidden="true" /></div>
          <div>
            <h2 id="upload-title">Import a puzzle</h2>
            <p>Start with a clear image of the grid.</p>
          </div>
          <button className="dialog-close" type="button" onClick={close} aria-label="Close upload dialog">
            <X size={19} aria-hidden="true" />
          </button>
        </header>

        {stage === 'complete' ? (
          <div className="upload-complete" role="status">
            <span className="complete-mark"><Check size={25} aria-hidden="true" /></span>
            <h3>Puzzle imported</h3>
            <p>{statusMessage}</p>
            <button className="upload-primary" type="button" onClick={close}>Done</button>
          </div>
        ) : (
          <>
            <div
              className={`upload-dropzone ${isDragging ? 'upload-dropzone-active' : ''} ${file ? 'upload-dropzone-selected' : ''}`}
              role="button"
              tabIndex={0}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={handleDropKeyDown}
              onDragOver={(event) => {
                event.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              aria-label="Choose or drop a puzzle image"
            >
              <input
                ref={fileInputRef}
                className="visually-hidden"
                type="file"
                accept=".png,.jpg,.jpeg,image/png,image/jpeg"
                onChange={handleFileChange}
                aria-label="Choose a puzzle image"
              />
              <span className="dropzone-icon"><FileImage size={23} strokeWidth={1.6} aria-hidden="true" /></span>
              {file ? (
                <span className="selected-file">
                  <strong>{file.name}</strong>
                  <span>{formatFileSize(file.size)} · click to change</span>
                </span>
              ) : (
                <span className="dropzone-copy">
                  <strong>Drop an image here</strong>
                  <span>or <span className="browse-link">browse files</span></span>
                </span>
              )}
              <span className="file-rules">PNG, JPG or JPEG <i /> up to 20 MB</span>
            </div>

            <div className={`upload-status ${stage === 'error' ? 'upload-status-error' : ''}`} aria-live="polite">
              {isBusy && <LoaderCircle size={15} className="spin" aria-hidden="true" />}
              {stage === 'error' && <X size={15} aria-hidden="true" />}
              {statusMessage}
            </div>

            <div className="upload-actions">
              <button className="upload-cancel" type="button" onClick={close} disabled={isBusy}>Cancel</button>
              <button className="upload-primary" type="button" onClick={upload} disabled={!file || isBusy}>
                {isBusy ? 'Working…' : stage === 'error' && file ? 'Try again' : 'Upload puzzle'}
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  )
}