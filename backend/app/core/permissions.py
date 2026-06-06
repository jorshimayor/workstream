"""Permission helpers for actor role checks."""

from __future__ import annotations

from app.schemas.auth import ActorContext


class PermissionDenied(Exception):
    """Raised when the current actor lacks required permissions."""


def require_any_role(actor: ActorContext, allowed_roles: set[str]) -> None:
    """Require the actor to hold at least one allowed role.

    Args:
        actor: Verified actor context for the current request.
        allowed_roles: Roles that can perform the protected operation.

    Raises:
        PermissionDenied: If the actor has none of the allowed roles.
    """
    if not set(actor.roles).intersection(allowed_roles):
        raise PermissionDenied("actor lacks required role")
