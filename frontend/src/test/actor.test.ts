import { ApiError } from '../api/client'
import type { ActorResponse } from '../api/types'
import { actorErrorLabel, actorName } from '../components/actor'

function actor(overrides: Partial<ActorResponse>): ActorResponse {
  return {
    actor_id: 'a1',
    external_subject: 'subject-1',
    external_issuer: 'iss',
    email: null,
    display_name: null,
    roles: [],
    auth_source: 'dev_mock',
    is_dev_auth: true,
    audit_context: {
      actor_id: 'a1',
      external_subject: 'subject-1',
      external_issuer: 'iss',
      actor_roles: [],
      claim_snapshot: {},
      auth_source: 'dev_mock',
      is_dev_auth: true,
    },
    ...overrides,
  }
}

describe('actorName', () => {
  it('uses display_name when present', () => {
    expect(actorName(actor({ display_name: 'Research Lead' }))).toBe('Research Lead')
  })

  it('falls back to email when display_name is empty or whitespace', () => {
    expect(actorName(actor({ display_name: '   ', email: 'lead@flow.dev' }))).toBe('lead@flow.dev')
  })

  it('falls back to external_subject when display_name and email are absent', () => {
    expect(actorName(actor({ display_name: '', email: null }))).toBe('subject-1')
  })
})

describe('actorErrorLabel', () => {
  it('reads a 401 as signed out', () => {
    expect(actorErrorLabel(new ApiError(401, 'Missing bearer token', 'x'))).toBe('signed out')
  })

  it('reads any other failure as unavailable', () => {
    expect(actorErrorLabel(new ApiError(503, null, 'x'))).toBe('unavailable')
    expect(actorErrorLabel(new Error('network down'))).toBe('unavailable')
  })
})
