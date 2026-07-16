"""Provider-neutral contracts for immutable artifact byte storage."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from app.interfaces.external_services import ExternalServiceAdapter
from app.modules.artifacts.sources import ArtifactCommitment, CommittedArtifactSource


_MAXIMUM_PROVIDER_OBJECT_REF_LENGTH = 1024


def _validate_provider_object_ref(provider_object_ref: str) -> None:
    """Require one bounded opaque provider reference without control characters."""
    if (
        not isinstance(provider_object_ref, str)
        or not provider_object_ref
        or len(provider_object_ref) > _MAXIMUM_PROVIDER_OBJECT_REF_LENGTH
        or any(ord(character) < 32 or ord(character) == 127 for character in provider_object_ref)
    ):
        raise ValueError("artifact provider object reference is invalid")


@dataclass(frozen=True, slots=True)
class ArtifactByteRange:
    """Zero-based byte range whose optional length defines an exclusive end."""

    offset: int = 0
    length: int | None = None

    def __post_init__(self) -> None:
        """Reject negative, boolean, and non-integer range values."""
        if type(self.offset) is not int or self.offset < 0:
            raise ValueError("artifact byte range offset is invalid")
        if self.length is not None and (type(self.length) is not int or self.length < 0):
            raise ValueError("artifact byte range length is invalid")


@dataclass(frozen=True, slots=True)
class ArtifactPutResult:
    """Provider-neutral result of immutable publication or an exact replay."""

    provider_object_ref: str
    replayed: bool

    def __post_init__(self) -> None:
        """Validate the bounded provider result."""
        _validate_provider_object_ref(self.provider_object_ref)
        if type(self.replayed) is not bool:
            raise ValueError("artifact put replay observation is invalid")


@dataclass(frozen=True, slots=True)
class ArtifactPutObservation:
    """Read-only exact observation of one commitment-derived provider object."""

    provider_object_ref: str
    committed: bool

    def __post_init__(self) -> None:
        """Validate the bounded provider observation."""
        _validate_provider_object_ref(self.provider_object_ref)
        if type(self.committed) is not bool:
            raise ValueError("artifact put observation is invalid")


@dataclass(frozen=True, slots=True)
class ArtifactObjectHead:
    """Safe provider observation for an existing or missing immutable object."""

    provider_object_ref: str
    exists: bool
    byte_count: int | None = None
    media_type: str | None = None

    def __post_init__(self) -> None:
        """Keep missing and existing head observations unambiguous."""
        _validate_provider_object_ref(self.provider_object_ref)
        if type(self.exists) is not bool:
            raise ValueError("artifact head existence observation is invalid")
        if self.exists:
            if type(self.byte_count) is not int or self.byte_count < 0:
                raise ValueError("existing artifact head requires an exact byte count")
        elif self.byte_count is not None or self.media_type is not None:
            raise ValueError("missing artifact head cannot contain object metadata")
        if self.media_type is not None:
            ArtifactCommitment.validate_media_type(self.media_type)


class ArtifactStoreError(Exception):
    """Base class for stable, provider-secret-safe artifact failures."""

    code = "artifact_storage_error"
    category = "terminal"
    retryable = False


class ArtifactStoreUnavailableError(ArtifactStoreError):
    """Raised when provider availability prevents an exact result."""

    code = "artifact_storage_unavailable"
    category = "retryable"
    retryable = True


class ArtifactObjectMissingError(ArtifactStoreError):
    """Raised when an operation requires an object that does not exist."""

    code = "artifact_object_missing"
    category = "not_found"


class ArtifactPreconditionFailedError(ArtifactStoreError):
    """Raised when immutable provider publication loses its condition."""

    code = "artifact_precondition_failed"
    category = "conflict"


class ArtifactInputMismatchError(ArtifactStoreError):
    """Raised when supplied bytes violate their server-owned commitment."""

    code = "artifact_input_mismatch"
    category = "input_mismatch"


class ArtifactIntegrityError(ArtifactStoreError):
    """Raised when provider or prepared bytes violate immutable facts."""

    code = "artifact_integrity_failure"
    category = "integrity"


class ArtifactRangeInvalidError(ArtifactStoreError):
    """Raised when a requested range starts past the object end."""

    code = "artifact_range_invalid"
    category = "input_mismatch"


class ArtifactOperationConflictError(ArtifactStoreError):
    """Raised when an opaque provider reference is invalid for an operation."""

    code = "artifact_operation_conflict"
    category = "conflict"


class ArtifactLimitExceededError(ArtifactStoreError):
    """Raised when bounded artifact input exceeds its hard limit."""

    code = "artifact_limit_exceeded"
    category = "terminal"


class ArtifactConfigurationError(ArtifactStoreError):
    """Raised when artifact adapter construction or selection is invalid."""

    code = "artifact_storage_configuration_invalid"
    category = "configuration"


class ArtifactStore(ExternalServiceAdapter, Protocol):
    """Immutable byte-provider capability used only by artifact orchestration."""

    async def put(self, source: CommittedArtifactSource) -> ArtifactPutResult:
        """Publish one sealed committed source or prove an exact replay."""

    async def observe_put_result(
        self,
        commitment: ArtifactCommitment,
    ) -> ArtifactPutObservation:
        """Observe one commitment-derived object without replaying a write."""

    def open(
        self,
        provider_object_ref: str,
        byte_range: ArtifactByteRange | None = None,
    ) -> AsyncIterator[bytes]:
        """Stream one object or bounded range in bounded chunks."""

    async def head(self, provider_object_ref: str) -> ArtifactObjectHead:
        """Return a safe existing or missing object observation."""
