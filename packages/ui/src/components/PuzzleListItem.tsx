import { useState } from 'react'
import { ArrowUpRight, Grid2X2, Trash2 } from 'lucide-react'
import { apiClient, type PuzzleSummary } from '../apiClient'

interface PuzzleListItemProps {
  puzzle: PuzzleSummary
  rowIndex: number
  onDelete: (puzzleId: string) => Promise<void>
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Date unavailable'
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(date)
}

export function PuzzleListItem({ puzzle, rowIndex, onDelete }: PuzzleListItemProps) {
  const [previewFailed, setPreviewFailed] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const confirmDelete = async () => {
    setDeleting(true)
    setDeleteError('')
    try {
      await onDelete(puzzle.id)
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : 'Unable to delete this puzzle.')
      setDeleting(false)
    }
  }

  return (
    <article className="puzzle-row" style={{ '--row-index': rowIndex } as React.CSSProperties}>
      <div className="puzzle-identity">
        {previewFailed ? (
          <span className="grid-preview grid-preview-fallback" aria-label="Grid preview unavailable">
            <Grid2X2 size={22} strokeWidth={1.5} aria-hidden="true" />
          </span>
        ) : (
          <img
            className="grid-preview"
            src={apiClient.getPuzzleGridImageUrl(puzzle.id)}
            alt={`Grid preview for ${puzzle.name}`}
            loading="lazy"
            onError={() => setPreviewFailed(true)}
          />
        )}
        <div className="puzzle-copy">
          <h2 title={puzzle.name}>{puzzle.name || 'Untitled puzzle'}</h2>
          <span className="puzzle-id">{puzzle.id}</span>
        </div>
      </div>
      <div className="clue-count">
        <span className="mobile-label">CLUES</span>
        <strong>{puzzle.clueCount}</strong>
        <span>clues</span>
      </div>
      <time className="added-date" dateTime={puzzle.createdAt}>
        <span className="mobile-label">ADDED</span>
        {formatDate(puzzle.createdAt)}
      </time>
      <div className="row-actions">
        <a
          className="open-grid"
          href={apiClient.getPuzzleGridImageUrl(puzzle.id)}
          target="_blank"
          rel="noreferrer"
          aria-label={`Open grid image for ${puzzle.name}`}
          title="Open grid image"
        >
          <span>View grid</span>
          <ArrowUpRight size={16} strokeWidth={1.8} aria-hidden="true" />
        </a>
        {confirmingDelete ? (
          <div className="delete-confirm" role="group" aria-label={`Delete ${puzzle.name}`}>
            {deleteError ? <span className="delete-error" role="alert">{deleteError}</span> : <span>Delete puzzle?</span>}
            <button className="delete-cancel" type="button" disabled={deleting} onClick={() => setConfirmingDelete(false)}>
              Cancel
            </button>
            <button
              className="delete-confirm-button"
              type="button"
              disabled={deleting}
              aria-label={`Confirm delete ${puzzle.name}`}
              onClick={confirmDelete}
            >
              {deleting ? 'Deleting…' : 'Delete'}
            </button>
          </div>
        ) : (
          <button
            className="delete-puzzle-button"
            type="button"
            aria-label={`Delete ${puzzle.name}`}
            title={`Delete ${puzzle.name}`}
            onClick={() => setConfirmingDelete(true)}
          >
            <Trash2 size={16} strokeWidth={1.8} aria-hidden="true" />
          </button>
        )}
      </div>
    </article>
  )
}