import { useEffect, useState } from 'react'
import { apiClient, type PuzzleSummary } from './apiClient'
import { PuzzleListPage, type PuzzleListLoadState } from './components/PuzzleListPage'
import './App.css'

function App() {
  const [puzzles, setPuzzles] = useState<PuzzleSummary[]>([])
  const [loadState, setLoadState] = useState<PuzzleListLoadState>('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    apiClient
      .getAllPuzzleSummaries(controller.signal)
      .then((results) => {
        setPuzzles(results)
        setLoadState('ready')
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        setErrorMessage(error instanceof Error ? error.message : 'Something went wrong while loading puzzles.')
        setLoadState('error')
      })

    return () => controller.abort()
  }, [reloadKey])

  const refresh = () => {
    setLoadState('loading')
    setErrorMessage('')
    setReloadKey((key) => key + 1)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Crossword Atlas home">
          <span className="brand-mark" aria-hidden="true"><span /><span /><span /><span /></span>
          <span className="brand-name">Crossword<span>Atlas</span></span>
        </a>
        <div className={`connection-state ${loadState === 'error' ? 'connection-error' : ''}`}>
          <span className="connection-dot" />
          <span>{loadState === 'error' ? 'Connection issue' : loadState === 'loading' ? 'Connecting' : 'Library synced'}</span>
        </div>
      </header>

      <PuzzleListPage puzzles={puzzles} loadState={loadState} errorMessage={errorMessage} onRefresh={refresh} />
      <footer className="app-footer"><span>Crossword Atlas</span><span>PUZZLE ARCHIVE <span className="footer-separator">/</span> 01</span></footer>
    </div>
  )
}

export default App
