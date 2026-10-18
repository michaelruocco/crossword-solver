import { useDeferredValue, useState } from 'react'
import { ArrowDownWideNarrow, Puzzle, RefreshCw, Search } from 'lucide-react'
import type { PuzzleSummary } from '../apiClient'
import { PuzzleListItem } from './PuzzleListItem'

export type PuzzleListLoadState = 'loading' | 'ready' | 'error'
type SortOrder = 'recent' | 'oldest' | 'most-clues'

interface PuzzleListPageProps {
  puzzles: PuzzleSummary[]
  loadState: PuzzleListLoadState
  errorMessage: string
  onRefresh: () => void
}

export function PuzzleListPage({ puzzles, loadState, errorMessage, onRefresh }: PuzzleListPageProps) {
  const [search, setSearch] = useState('')
  const [sortOrder, setSortOrder] = useState<SortOrder>('recent')
  const deferredSearch = useDeferredValue(search)
  const normalizedSearch = deferredSearch.trim().toLocaleLowerCase()
  const visiblePuzzles = puzzles
    .filter((puzzle) => puzzle.name.toLocaleLowerCase().includes(normalizedSearch))
    .sort((first, second) => {
      if (sortOrder === 'most-clues') return second.clueCount - first.clueCount
      const dateDifference = new Date(first.createdAt).getTime() - new Date(second.createdAt).getTime()
      return sortOrder === 'oldest' ? dateDifference : -dateDifference
    })

  return (
    <main className="main-content">
      <section className="page-heading" aria-labelledby="page-title">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> YOUR COLLECTION</div>
          <h1 id="page-title">Puzzle library</h1>
          <p className="page-subtitle">Every grid, ready to revisit.</p>
        </div>
        <div className="collection-stat" aria-live="polite">
          <span className="stat-number">{loadState === 'ready' ? puzzles.length : '—'}</span>
          <span className="stat-label">{puzzles.length === 1 ? 'puzzle' : 'puzzles'} in library</span>
        </div>
      </section>

      <section className="library" aria-label="Puzzle summaries">
        <div className="library-toolbar">
          <label className="search-box">
            <Search size={18} strokeWidth={1.8} aria-hidden="true" />
            <span className="visually-hidden">Search puzzles</span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Find a puzzle by name"
            />
            {search && <span className="result-count">{visiblePuzzles.length} found</span>}
          </label>

          <div className="toolbar-actions">
            <label className="sort-control">
              <ArrowDownWideNarrow size={17} strokeWidth={1.8} aria-hidden="true" />
              <span className="visually-hidden">Sort puzzles</span>
              <select value={sortOrder} onChange={(event) => setSortOrder(event.target.value as SortOrder)}>
                <option value="recent">Recently added</option>
                <option value="oldest">Oldest first</option>
                <option value="most-clues">Most clues</option>
              </select>
            </label>
            <button
              className="icon-button"
              type="button"
              onClick={onRefresh}
              disabled={loadState === 'loading'}
              title="Refresh puzzles"
              aria-label="Refresh puzzles"
            >
              <RefreshCw size={17} className={loadState === 'loading' ? 'spin' : ''} aria-hidden="true" />
            </button>
          </div>
        </div>

        <div className="list-heading" aria-hidden="true">
          <span>PUZZLE</span>
          <span>CLUES</span>
          <span>ADDED</span>
          <span />
        </div>

        {loadState === 'loading' && (
          <div className="loading-list" aria-label="Loading puzzles" aria-live="polite">
            {Array.from({ length: 4 }, (_, index) => (
              <div className="skeleton-row" key={index}>
                <span className="skeleton-thumb" />
                <span className="skeleton-title" />
                <span className="skeleton-meta" />
              </div>
            ))}
          </div>
        )}

        {loadState === 'error' && (
          <div className="state-panel error-panel" role="alert">
            <div className="state-icon state-icon-error"><RefreshCw size={21} aria-hidden="true" /></div>
            <h2>Couldn’t load your puzzles</h2>
            <p>{errorMessage}</p>
            <button type="button" className="retry-button" onClick={onRefresh}>Try again</button>
          </div>
        )}

        {loadState === 'ready' && visiblePuzzles.length > 0 && (
          <div className="puzzle-list">
            {visiblePuzzles.map((puzzle, index) => (
              <PuzzleListItem key={puzzle.id} puzzle={puzzle} rowIndex={index} />
            ))}
          </div>
        )}

        {loadState === 'ready' && visiblePuzzles.length === 0 && (
          <div className="state-panel empty-panel">
            <div className="state-icon"><Puzzle size={22} strokeWidth={1.6} aria-hidden="true" /></div>
            <h2>{search ? 'No matching puzzles' : 'Your library is empty'}</h2>
            <p>{search ? 'Try a different name or clear your search.' : 'Imported puzzles will appear here.'}</p>
            {search && <button className="text-button" type="button" onClick={() => setSearch('')}>Clear search</button>}
          </div>
        )}

        {loadState === 'ready' && puzzles.length > 0 && visiblePuzzles.length > 0 && (
          <footer className="list-footer">
            <span>Showing <strong>{visiblePuzzles.length}</strong> of <strong>{puzzles.length}</strong> puzzles</span>
            <span className="footer-mark"><span /> A quieter place for good puzzles</span>
          </footer>
        )}
      </section>
    </main>
  )
}