import { getToken } from '../auth/token'

const DEFAULT_BASE = '/api/v1'

export function apiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL
  return typeof configured === 'string' && configured.length > 0 ? configured : DEFAULT_BASE
}

// A single typed error shape for every non-2xx backend response.
export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')

  const token = getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${apiBaseUrl()}${path}`, { ...init, headers })

  if (!response.ok) {
    let detail: unknown = null
    try {
      const body = (await response.json()) as { detail?: unknown }
      detail = body?.detail ?? body
    } catch {
      detail = null
    }
    throw new ApiError(response.status, detail, `Request to ${path} failed with ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
