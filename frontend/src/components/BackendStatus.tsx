import type { ActorResponse, HealthResponse } from '../api/types'
import type { AsyncState } from '../api/useAsync'
import { actorErrorLabel, actorName } from './actor'

interface BackendStatusProps {
  health: AsyncState<HealthResponse>
  actor: AsyncState<ActorResponse>
}

// A thin mono strip that proves the /api/v1 connection: backend health on the
// left, the resolved actor (or signed-out state) on the right.
export function BackendStatus({ health, actor }: BackendStatusProps) {
  return (
    <div className="status-strip">
      <span>
        {'api: '}
        {health.status === 'loading' && <span className="mono-muted">checking</span>}
        {health.status === 'ok' && <span className="state-ready">{health.data.status}</span>}
        {health.status === 'error' && <span className="state-rejected">unreachable</span>}
      </span>
      <span className="status-sep">/</span>
      <span>
        {'actor: '}
        {actor.status === 'loading' && <span className="mono-muted">resolving</span>}
        {actor.status === 'ok' && <span className="state-ready">{actorSummary(actor.data)}</span>}
        {actor.status === 'error' && (
          <span className="mono-muted">{actorErrorLabel(actor.error)}</span>
        )}
      </span>
    </div>
  )
}

function actorSummary(actor: ActorResponse): string {
  const roles = actor.roles.length > 0 ? ` · ${actor.roles.join(', ')}` : ''
  return `${actorName(actor)}${roles}`
}
