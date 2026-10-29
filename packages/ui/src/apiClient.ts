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

export interface PuzzleUploadPost {
  url: string
  fields: Record<string, string>
}

export interface PuzzleUploadResponse {
  id: string
  upload: PuzzleUploadPost
}

export interface PuzzleImportStatus {
  id: string
  status: 'AWAITING_UPLOAD' | 'PENDING' | 'COMPLETE' | 'FAILED'
  puzzleId: string | null
  error: string | null
}

export class ApiClient {
  private readonly baseUrl: string

  constructor(baseUrl: string) {
    let end = baseUrl.length
    while (end > 0 && baseUrl[end - 1] === '/') end--
    this.baseUrl = baseUrl.slice(0, end)
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
    return this.collectPuzzleSummaries(null, new Set<string>(), signal)
  }

  private async collectPuzzleSummaries(cursor: string | null, seenCursors: Set<string>, signal?: AbortSignal): Promise<PuzzleSummary[]> {
    const page = await this.getPuzzleSummaryPage({ limit: 100, cursor, signal })
    const next = page.nextCursor
    if (!next) return page.summaries

    if (seenCursors.has(next)) throw new Error('Puzzle API returned a repeated pagination cursor.')
    seenCursors.add(next)
    return [...page.summaries, ...(await this.collectPuzzleSummaries(next, seenCursors, signal))]
  }

  async startPuzzleImport(imageUrl: string, signal?: AbortSignal): Promise<{ location: string }> {
    const response = await fetch(this.endpoint('/v1/puzzles/imports'), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ imageUrl }),
      signal,
    })
    const result = await this.readJson<{ id: string }>(response, 'Unable to start puzzle import.')
    return {
      location: response.headers.get('location') ?? `/v1/puzzles/imports/${encodeURIComponent(result.id)}`,
    }
  }

  async startPuzzleUpload(fileName: string, signal?: AbortSignal): Promise<{ upload: PuzzleUploadPost; location: string }> {
    const response = await fetch(this.endpoint('/v1/puzzles/uploads'), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ fileName }),
      signal,
    })
    const result = await this.readJson<PuzzleUploadResponse>(response, 'Unable to start puzzle upload.')

    return {
      upload: result.upload,
      location: response.headers.get('location') ?? `/v1/puzzles/imports/${encodeURIComponent(result.id)}`,
    }
  }

  async uploadPuzzleFile(upload: PuzzleUploadPost, file: File, signal?: AbortSignal): Promise<void> {
    const formData = new FormData()
    for (const [name, value] of Object.entries(upload.fields)) formData.append(name, value)
    formData.append('file', file)

    const response = await fetch(upload.url, { method: 'POST', body: formData, signal })
    if (!response.ok) throw new Error(`S3 rejected the upload with status ${response.status}.`)
  }

  async getPuzzleImport(location: string, signal?: AbortSignal): Promise<PuzzleImportStatus> {
    const url = new URL(location, this.baseUrl || window.location.origin)
    const response = await fetch(url, { signal })
    return this.readJson<PuzzleImportStatus>(response, 'Unable to read puzzle import status.')
  }

  async waitForPuzzleImport(location: string, signal?: AbortSignal, attempt = 0): Promise<PuzzleImportStatus> {
    if (attempt >= 180) {
      throw new Error('Puzzle import is taking longer than expected. Check the puzzle library again shortly.')
    }

    const result = await this.getPuzzleImport(location, signal)
    if (result.status === 'COMPLETE') return result
    if (result.status === 'FAILED') throw new Error(result.error ?? 'Puzzle import failed.')
    await new Promise((resolve) => window.setTimeout(resolve, 1000))
    return this.waitForPuzzleImport(location, signal, attempt + 1)
  }

  async deletePuzzle(puzzleId: string, signal?: AbortSignal): Promise<void> {
    const response = await fetch(this.endpoint(`/v1/puzzles/${encodeURIComponent(puzzleId)}`), {
      method: 'DELETE',
      signal,
    })
    if (!response.ok) throw await this.responseError(response, 'Unable to delete puzzle.')
  }

  getPuzzleGridImageUrl(puzzleId: string): string {
    return this.endpoint(`/v1/puzzles/${encodeURIComponent(puzzleId)}/grid-images`)
  }

  private endpoint(path: string): string {
    return `${this.baseUrl}${path}`
  }

  private async readJson<T>(response: Response, fallback: string): Promise<T> {
    if (!response.ok) throw await this.responseError(response, fallback)
    return (await response.json()) as T
  }

  private async responseError(response: Response, fallback: string): Promise<Error> {
    try {
      const body = (await response.json()) as { message?: unknown }
      if (typeof body.message === 'string' && body.message.length > 0) return new Error(body.message)
    } catch {
      return new Error(fallback)
    }
    return new Error(fallback)
  }
}

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''
export const apiClient = new ApiClient(configuredBaseUrl)