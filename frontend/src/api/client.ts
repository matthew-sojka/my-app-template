export class ApiError extends Error {
  readonly status: number
  /** Parsed JSON error body, if the server sent one (e.g. FastAPI's `{ detail }`). */
  readonly body: unknown

  constructor(status: number, message: string, body: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

/** GET a JSON endpoint, throwing on non-2xx so TanStack Query treats it as an error. */
export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } })
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => undefined)
    throw new ApiError(response.status, `GET ${path} failed: ${response.status}`, body)
  }
  return (await response.json()) as T
}
