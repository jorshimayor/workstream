"""Pydantic schemas for actor profile APIs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_skill_tags(value: list[str]) -> list[str]:
    """Normalize actor skill tags to stable lowercase tokens.

    Args:
        value: Client or service supplied skill tags.

    Returns:
        Deduplicated normalized skill tags.

    Raises:
        ValueError: If any tag is empty or too long.
    """
    normalized_tags: list[str] = []
    seen_tags: set[str] = set()
    for raw_tag in value:
        tag = raw_tag.strip().lower()
        if not tag:
            raise ValueError("skill_tags cannot include empty values")
        if len(tag) > 64:
            raise ValueError("skill_tags values must be 64 characters or fewer")
        if tag not in seen_tags:
            normalized_tags.append(tag)
            seen_tags.add(tag)
    return normalized_tags


class ActorProfileActivationRequest(BaseModel):
    """Request schema for explicitly activating the current actor's profile."""

    model_config = ConfigDict(extra="forbid")

    skill_tags: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("skill_tags")
    @classmethod
    def validate_skill_tags(cls, value: list[str]) -> list[str]:
        """Normalize profile skill tags before persistence."""
        return normalize_skill_tags(value)


class ActorProfileResponse(BaseModel):
    """Response schema for a profile joined to token-derived identity metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str
    profile_type: str
    status: str
    skill_tags: list[str]
    scope_type: str
    scope_id: str
    profile_metadata: dict
    external_subject: str
    external_issuer: str
    display_name: str | None
    email: str | None
    created_at: datetime
    updated_at: datetime
