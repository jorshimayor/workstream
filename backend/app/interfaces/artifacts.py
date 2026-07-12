"""Provider-neutral contracts for immutable artifact storage."""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from app.core.hashing import canonical_json_hash


class ArtifactOperation(StrEnum):
    """Storage operations with independent idempotency scopes."""

    STORE = "store"
    VERIFY = "verify"
    RETAIN = "retain"
    RELEASE = "release"


class VerificationState(StrEnum):
    """Provider observation of full-object verification."""

    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class RetentionState(StrEnum):
    """Provider observation of active retention references."""

    UNRETAINED = "unretained"
    RETAINED = "retained"
    RELEASED = "released"


class AvailabilityState(StrEnum):
    """Provider observation of object availability."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MISSING = "missing"


class IntegrityState(StrEnum):
    """Provider observation of object integrity."""

    UNKNOWN = "unknown"
    VALID = "valid"
    QUARANTINED = "quarantined"


class ReceiptOutcome(StrEnum):
    """Successful immutable provider operation facts."""

    STORED = "stored"
    VERIFIED = "verified"
    RETAINED = "retained"
    RELEASED = "released"


@dataclass(frozen=True, slots=True)
class IdempotencyIdentity:
    """Complete identity and commitment for one provider operation."""

    service_principal: str
    operation: ArtifactOperation
    key: str
    request_digest: str


@dataclass(frozen=True, slots=True)
class ArtifactByteRange:
    """Zero-based byte range with an exclusive end."""

    offset: int = 0
    length: int | None = None

    def __post_init__(self) -> None:
        """Reject negative offsets and lengths."""
        if self.offset < 0 or (self.length is not None and self.length < 0):
            raise ValueError("artifact byte range values must be nonnegative")


@dataclass(frozen=True, slots=True)
class StoreArtifactRequest:
    """Immutable metadata for one streamed store operation."""

    expected_sha256: str | None
    expected_size: int | None
    maximum_bytes: int
    media_type: str
    metadata: Mapping[str, str]
    idempotency: IdempotencyIdentity


@dataclass(frozen=True, slots=True)
class ReceiptDetail:
    """One bounded provider receipt detail entry."""

    name: str
    value: str


@dataclass(frozen=True, slots=True)
class OperationReceipt:
    """Bounded provider evidence for one authoritative operation."""

    receipt_id: str
    provider_operation_reference: str
    identity: IdempotencyIdentity
    response_digest: str
    outcome: ReceiptOutcome
    provider_artifact_id: str | None
    sha256: str | None
    byte_count: int | None
    recorded_at: datetime
    retention_reference: str | None = None
    retention_class: str | None = None
    details: tuple[ReceiptDetail, ...] = ()


@dataclass(frozen=True, slots=True)
class RetentionSummary:
    """One provider retention reference and its current state."""

    retention_reference: str
    retention_class: str
    state: str


@dataclass(frozen=True, slots=True)
class StoredArtifact:
    """Provider-neutral result of a successful store operation."""

    provider_artifact_id: str
    sha256: str
    byte_count: int
    media_type: str
    receipt: OperationReceipt
    replayed: bool


@dataclass(frozen=True, slots=True)
class ArtifactOperationResult:
    """One immutable receipt plus response-time replay information."""

    receipt: OperationReceipt
    replayed: bool


@dataclass(frozen=True, slots=True)
class ArtifactStatus:
    """Current provider observations for an immutable object."""

    provider_artifact_id: str
    sha256: str
    byte_count: int
    media_type: str
    verification_state: VerificationState
    retention_state: RetentionState
    availability_state: AvailabilityState
    integrity_state: IntegrityState
    active_retentions: tuple[RetentionSummary, ...] = ()


class ArtifactStoreError(Exception):
    """Base class for stable artifact-store failures."""

    code = "artifact_storage_error"
    category = "terminal"
    retryable = False


class ArtifactStoreUnavailableError(ArtifactStoreError):
    """Raised when a retryable provider operation is unavailable."""

    code = "artifact_storage_unavailable"
    category = "retryable"
    retryable = True


class ArtifactMalformedRequestError(ArtifactStoreError):
    """Raised when a provider request is structurally invalid."""

    code = "artifact_malformed_request"


class ArtifactInputMismatchError(ArtifactStoreError):
    """Raised when supplied bytes violate their initial commitment."""

    code = "artifact_input_mismatch"
    category = "input_mismatch"


class ArtifactLimitExceededError(ArtifactStoreError):
    """Raised when bounded artifact input exceeds a declared limit."""

    code = "artifact_limit_exceeded"
    category = "terminal"


class ArtifactIntegrityError(ArtifactStoreError):
    """Raised when persisted or replayed provider facts are inconsistent."""

    code = "artifact_integrity_failure"
    category = "integrity"


class ArtifactIdempotencyMismatchError(ArtifactStoreError):
    """Raised when one operation identity is reused with a changed request."""

    code = "artifact_idempotency_mismatch"


class ArtifactNotFoundError(ArtifactStoreError):
    """Raised when an opaque provider artifact is unknown or unavailable."""

    code = "artifact_not_found"
    category = "not_found"


class ArtifactRetentionConflictError(ArtifactStoreError):
    """Raised when an exact retention reference cannot be changed."""

    code = "artifact_retention_conflict"
    category = "input_mismatch"


class ArtifactThrottledError(ArtifactStoreError):
    """Raised when a retryable provider throttle prevents an operation."""

    code = "artifact_throttled"
    category = "retryable"
    retryable = True


class ArtifactConfigurationError(ArtifactStoreError):
    """Raised when a configured artifact adapter cannot be resolved."""

    code = "artifact_storage_configuration_invalid"


class ArtifactStore(Protocol):
    """Port implemented by development and production artifact providers."""

    async def store(
        self,
        stream: AsyncIterable[bytes],
        request: StoreArtifactRequest,
    ) -> StoredArtifact:
        """Store one bounded stream or return its exact replay result."""

    async def recover_committed_store(
        self, request: StoreArtifactRequest
    ) -> StoredArtifact:
        """Recover one committed store effect from exact persisted commitments."""

    def open(
        self,
        provider_artifact_id: str,
        byte_range: ArtifactByteRange | None = None,
    ) -> AsyncIterator[bytes]:
        """Stream one available object or range in bounded chunks."""

    async def stat(self, provider_artifact_id: str) -> ArtifactStatus:
        """Return current provider observations for one object."""

    async def verify(
        self,
        provider_artifact_id: str,
        expected_sha256: str,
        expected_size: int,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Independently hash and count one complete provider object."""

    async def retain(
        self,
        provider_artifact_id: str,
        retention_reference: str,
        retention_class: str,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Add an exact reference-counted retention intent."""

    async def release(
        self,
        provider_artifact_id: str,
        retention_reference: str,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Release only the exact retention reference supplied."""

    async def get_operation_receipt(
        self,
        service_principal: str,
        operation: ArtifactOperation,
        idempotency_key: str,
    ) -> OperationReceipt | None:
        """Load the authoritative receipt for one complete operation identity."""


def canonical_store_request_digest(request: StoreArtifactRequest) -> str:
    """Return the canonical digest for all authoritative store request fields."""
    payload: dict[str, object] = {
        "maximum_bytes": request.maximum_bytes,
        "media_type": request.media_type,
        "metadata": [
            {"name": name, "value": value}
            for name, value in sorted(request.metadata.items())
        ],
    }
    if request.expected_sha256 is not None:
        payload["expected_sha256"] = request.expected_sha256
    if request.expected_size is not None:
        payload["expected_size"] = request.expected_size
    return canonical_json_hash(payload)


def canonical_verify_request_digest(
    provider_artifact_id: str, expected_sha256: str, expected_size: int
) -> str:
    """Return the canonical digest for one verify request."""
    return canonical_json_hash(
        {
            "provider_artifact_id": provider_artifact_id,
            "expected_sha256": expected_sha256,
            "expected_size": expected_size,
        }
    )


def canonical_retain_request_digest(
    provider_artifact_id: str, retention_reference: str, retention_class: str
) -> str:
    """Return the canonical digest for one retain request."""
    return canonical_json_hash(
        {
            "provider_artifact_id": provider_artifact_id,
            "retention_reference": retention_reference,
            "retention_class": retention_class,
        }
    )


def canonical_release_request_digest(
    provider_artifact_id: str, retention_reference: str
) -> str:
    """Return the canonical digest for one release request."""
    return canonical_json_hash(
        {
            "provider_artifact_id": provider_artifact_id,
            "retention_reference": retention_reference,
        }
    )
