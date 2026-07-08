import { Link, NavLink } from 'react-router-dom'
import type { ActorResponse } from '../api/types'
import type { AsyncState } from '../api/useAsync'
import { SURFACES } from '../routes/surfaces'
import { actorErrorLabel, actorName } from './actor'

interface NavShellProps {
  actor: AsyncState<ActorResponse>
}

export function NavShell({ actor }: NavShellProps) {
  return (
    <header className="nav">
      <Link to="/" className="nav-wordmark">
        <span className="nav-mark" aria-hidden="true" />
        Workstream
      </Link>
      <nav className="nav-links" aria-label="Primary">
        {SURFACES.map((surface) => (
          <NavLink
            key={surface.path}
            to={surface.path}
            className={({ isActive }) => (isActive ? 'nav-link is-active' : 'nav-link')}
          >
            {surface.label}
          </NavLink>
        ))}
      </nav>
      <div className="nav-right">
        <span className="mono mono-muted">{navActorLabel(actor)}</span>
        <span className="command-trigger" aria-hidden="true">
          :
        </span>
      </div>
    </header>
  )
}

function navActorLabel(actor: AsyncState<ActorResponse>): string {
  if (actor.status === 'ok') return actorName(actor.data)
  if (actor.status === 'error') return actorErrorLabel(actor.error)
  return 'resolving'
}
