// Flow-style bearer token handling. Workstream owns no login or session; it only
// carries a token issued elsewhere. In dev the token comes from an env var or is
// pasted into local storage. Nothing here persists credentials server-side.

const STORAGE_KEY = 'workstream_token'

export function getToken(): string | null {
  const fromEnv = import.meta.env.VITE_WORKSTREAM_TOKEN
  if (typeof fromEnv === 'string' && fromEnv.length > 0) {
    return fromEnv
  }
  try {
    return window.localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, token)
  } catch {
    // Storage may be unavailable (private mode); ignore.
  }
}

export function clearToken(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Ignore storage errors.
  }
}
