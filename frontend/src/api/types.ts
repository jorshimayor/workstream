// Types mirror the backend Pydantic response schemas under app/schemas.

export type AuthSource = 'flow' | 'dev_mock' | 'workstream_system'

export interface HealthResponse {
  status: string
}

export interface ActorAuditContext {
  actor_id: string
  external_subject: string
  external_issuer: string
  actor_roles: string[]
  claim_snapshot: Record<string, unknown>
  auth_source: AuthSource
  is_dev_auth: boolean
}

export interface ActorResponse {
  actor_id: string
  external_subject: string
  external_issuer: string
  email: string | null
  display_name: string | null
  roles: string[]
  auth_source: AuthSource
  is_dev_auth: boolean
  audit_context: ActorAuditContext
}
