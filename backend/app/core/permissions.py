from __future__ import annotations

from app.schemas.auth import ActorContext


class PermissionDenied(Exception):
    """Raised when the current actor lacks required permissions."""


def require_any_role(actor: ActorContext, allowed_roles: set[str]) -> None:
    if not set(actor.roles).intersection(allowed_roles):
        raise PermissionDenied(
            f"actor lacks required role: has {actor.roles}, needs one of {sorted(allowed_roles)}"
        )
