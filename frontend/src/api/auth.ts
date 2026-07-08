import { apiFetch } from './client'
import type { ActorResponse } from './types'

export function getCurrentActor(): Promise<ActorResponse> {
  return apiFetch<ActorResponse>('/auth/me')
}
