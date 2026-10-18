import { useState } from 'react'
import { ArrowUpRight, Grid2X2 } from 'lucide-react'
import { apiClient, type PuzzleSummary } from '../apiClient'

interface PuzzleListItemProps {
  puzzle: PuzzleSummary
  rowIndex: number
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Date unavailable'
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(date)
}

export function PuzzleListItem({ puzzle, rowIndex }: PuzzleListItemProps) {
  const [previewFailed, setPreviewFailed] = useState(false)

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
    </article>
  )
}