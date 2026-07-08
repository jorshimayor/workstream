import { ApiError } from '../api/client'
import type { ActorResponse } from '../api/types'

// Prefer a human-facing name, falling back to the stable external subject.
export function actorName(actor: ActorResponse): string {
  return actor.display_name ?? actor.email ?? actor.external_subject
}

// Shared so the nav and the status strip label an actor error the same way:
// a 401 means no valid token (signed out); anything else is a backend problem.
export function actorErrorLabel(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) return 'signed out'
  return 'unavailable'
}
