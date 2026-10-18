export interface PuzzleSummary {
  id: string
  name: string
  createdAt: string
  clueCount: number
}

export interface PuzzleSummaryPage {
  summaries: PuzzleSummary[]
  nextCursor: string | null
}

export interface PuzzleSummaryPageOptions {
  limit?: number
  cursor?: string | null
  signal?: AbortSignal
}

export class ApiClient {
  private readonly baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '')
  }

  async getPuzzleSummaryPage({ limit = 100, cursor, signal }: PuzzleSummaryPageOptions = {}): Promise<PuzzleSummaryPage> {
    const url = new URL(this.endpoint('/v1/puzzle-summaries'), window.location.origin)
    url.searchParams.set('limit', String(limit))
    if (cursor) url.searchParams.set('cursor', cursor)

    const response = await fetch(url, { signal })
    if (!response.ok) throw new Error(`Puzzle API returned ${response.status} while loading summaries.`)
    return (await response.json()) as PuzzleSummaryPage
  }

  async getAllPuzzleSummaries(signal?: AbortSignal): Promise<PuzzleSummary[]> {
    const summaries: PuzzleSummary[] = []
    const seenCursors = new Set<string>()
    let cursor: string | null = null

    do {
      const page = await this.getPuzzleSummaryPage({ limit: 100, cursor, signal })
      summaries.push(...page.summaries)
      cursor = page.nextCursor

      if (cursor && seenCursors.has(cursor)) throw new Error('Puzzle API returned a repeated pagination cursor.')
      if (cursor) seenCursors.add(cursor)
    } while (cursor)

    return summaries
  }

  getPuzzleGridImageUrl(puzzleId: string): string {
    return this.endpoint(`/v1/puzzles/${encodeURIComponent(puzzleId)}/grid-images`)
  }

  private endpoint(path: string): string {
    return `${this.baseUrl}${path}`
  }
}

const configuredBaseUrl = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL ?? ''
export const apiClient = new ApiClient(configuredBaseUrl)