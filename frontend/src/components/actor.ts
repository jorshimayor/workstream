import { ApiError } from '../api/client'
import type { ActorResponse } from '../api/types'

// Prefer a human-facing name, falling back to the stable external subject.
// Treats empty/whitespace values as absent so a blank display_name doesn't
// short-circuit the fallback chain and render an empty label.
export function actorName(actor: ActorResponse): string {
  return firstNonEmpty(actor.display_name, actor.email) ?? actor.external_subject
}

function firstNonEmpty(...values: (string | null | undefined)[]): string | undefined {
  for (const value of values) {
    const trimmed = value?.trim()
    if (trimmed) return trimmed
  }
  return undefined
}

// Shared so the nav and the status strip label an actor error the same way:
// a 401 means no valid token (signed out); anything else is a backend problem.
export function actorErrorLabel(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) return 'signed out'
  return 'unavailable'
}
