"""Real MinIO and focused protocol tests for S3CompatibleArtifactStore."""

from __future__ import annotations

from contextlib import asynccontextmanager
import hashlib
import os
from pathlib import Path
from typing import Any

from aiobotocore.config import AioConfig
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError
import pytest

from app.adapters.artifacts import create_artifact_store_bootstrap
from app.adapters.artifacts.s3_compatible import (
    S3CompatibleArtifactStore,
    S3CompatibleArtifactStoreBootstrap,
)
import app.adapters.artifacts.s3_compatible as s3_module
from app.core.config import Settings
from app.interfaces.artifacts import (
    ArtifactByteRange,
    ArtifactConfigurationError,
    ArtifactIntegrityError,
    ArtifactInputMismatchError,
    ArtifactObjectMissingError,
    ArtifactOperationConflictError,
    ArtifactStore,
    ArtifactStoreNamespaceClaim,
    ArtifactStoreUnavailableError,
    artifact_store_namespace_material,
)
from app.interfaces.external_services import ExternalServiceAdapterIdentity
from tests.artifact_store_helpers import minted_source
from tests.test_artifact_store_conformance import ArtifactStoreConformanceTests


MINIO_ENDPOINT = os.environ.get("WORKSTREAM_TEST_MINIO_ENDPOINT", "http://localhost:9000")
MINIO_REGION = "us-east-1"
MINIO_BUCKET = "workstream-artifacts"
MINIO_ACCESS_KEY = "workstream-minio"
MINIO_SECRET_KEY = "workstream-minio-secret-key"


@pytest.fixture(scope="module", autouse=True)
async def provision_minio_bucket() -> None:
    """Provision only the dedicated integration bucket with MinIO admin credentials."""
    session = AioSession()
    session.set_credentials(MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    async with session.create_client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        region_name=MINIO_REGION,
        config=AioConfig(s3={"addressing_style": "path"}),
    ) as client:
        try:
            await client.create_bucket(Bucket=MINIO_BUCKET)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") not in {
                "BucketAlreadyExists",
                "BucketAlreadyOwnedByYou",
            }:
                raise


class TestMinioArtifactStoreConformance(ArtifactStoreConformanceTests):
    """Run the same ArtifactStore v2 vectors against real MinIO."""

    expected_identity = ExternalServiceAdapterIdentity(
        "artifact_store",
        "s3_compatible",
    )

    def make_store(self, root: Path) -> ArtifactStore:
        """Construct one namespace-isolated real MinIO adapter."""
        namespace = hashlib.sha256(os.fspath(root.parent).encode()).hexdigest()[:20]
        return initialize_minio_store(private_prefix=f"conformance/{namespace}")


def minio_settings(
    *,
    private_prefix: str,
    access_key: str = MINIO_ACCESS_KEY,
    secret_key: str = MINIO_SECRET_KEY,
) -> Settings:
    """Return one complete local-only MinIO configuration."""
    return Settings(
        environment="test",
        artifact_store_backend="s3_compatible",
        artifact_scratch_root=Path("/tmp/workstream-test-artifact-scratch"),
        artifact_s3_provider_profile="minio",
        artifact_s3_region=MINIO_REGION,
        artifact_s3_endpoint_url=MINIO_ENDPOINT,
        artifact_s3_bucket=MINIO_BUCKET,
        artifact_s3_private_prefix=private_prefix,
        artifact_s3_addressing_style="path",
        artifact_s3_credential_mode="local_static",
        artifact_s3_access_key_id=access_key,
        artifact_s3_secret_access_key=secret_key,
        artifact_stream_buffer_bytes=2,
        artifact_s3_operation_total_timeout_seconds=20,
        artifact_s3_write_timeout_seconds=20,
    )


def initialize_minio_store(*, private_prefix: str) -> S3CompatibleArtifactStore:
    """Construct, claim, and initialize one MinIO namespace."""
    bootstrap = create_artifact_store_bootstrap(
        minio_settings(private_prefix=private_prefix)
    )
    assert type(bootstrap) is S3CompatibleArtifactStoreBootstrap
    namespace_identity = bootstrap.namespace_identity
    _, fingerprint = artifact_store_namespace_material(
        backend="s3_compatible",
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace_identity,
    )
    return bootstrap.initialize_after_namespace_claim(
        ArtifactStoreNamespaceClaim(
            adapter_identity=bootstrap.identity,
            namespace_identity=namespace_identity,
            namespace_fingerprint=fingerprint,
        )
    )


@pytest.mark.asyncio
async def test_wrong_minio_credentials_map_403_to_unavailable() -> None:
    """Never misclassify forbidden provider access as authoritative absence."""
    settings = minio_settings(
        private_prefix="negative/forbidden",
        access_key="unknown-minio-user",
        secret_key="unknown-minio-password",
    )
    bootstrap = create_artifact_store_bootstrap(settings)
    namespace = bootstrap.namespace_identity
    _, fingerprint = artifact_store_namespace_material(
        backend="s3_compatible",
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace,
    )
    store = bootstrap.initialize_after_namespace_claim(
        ArtifactStoreNamespaceClaim(bootstrap.identity, namespace, fingerprint)
    )
    try:
        with pytest.raises(ArtifactStoreUnavailableError):
            await store.head("sha256/00/" + "0" * 62)
    finally:
        bootstrap.close()


@pytest.mark.asyncio
async def test_adversarial_first_writer_cannot_be_accepted_as_replay(
    tmp_path: Path,
) -> None:
    """Reject existing wrong bytes at the server-derived content key."""
    private_prefix = f"adversarial/{hashlib.sha256(os.urandom(16)).hexdigest()[:20]}"
    content = b"expected exact bytes"
    digest = hashlib.sha256(content).hexdigest()
    key = f"{private_prefix}/sha256/{digest[:2]}/{digest[2:]}"
    await raw_minio_put(key, b"attacker-selected wrong bytes")
    store = initialize_minio_store(private_prefix=private_prefix)
    try:
        async with minted_source(tmp_path / "scratch", content) as source:
            with pytest.raises(ArtifactIntegrityError):
                await store.put(source)
    finally:
        store.close()


@pytest.mark.asyncio
async def test_cross_project_prefix_cannot_occupy_another_content_key(
    tmp_path: Path,
) -> None:
    """Keep identical digest references isolated by claimed project namespace."""
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:20]
    attacker_prefix = f"projects/attacker-{nonce}"
    target_prefix = f"projects/target-{nonce}"
    content = b"target project exact bytes"
    digest = hashlib.sha256(content).hexdigest()
    provider_ref = f"sha256/{digest[:2]}/{digest[2:]}"
    await raw_minio_put(f"{attacker_prefix}/{provider_ref}", b"attacker bytes")

    attacker_store = initialize_minio_store(private_prefix=attacker_prefix)
    target_store = initialize_minio_store(private_prefix=target_prefix)
    try:
        async with minted_source(tmp_path / "attacker-scratch", content) as source:
            with pytest.raises(ArtifactIntegrityError):
                await attacker_store.put(source)
        async with minted_source(tmp_path / "target-scratch", content) as source:
            result = await target_store.put(source)
        assert result.provider_object_ref == provider_ref
        assert result.replayed is False
        assert b"".join([chunk async for chunk in target_store.open(provider_ref)]) == content
    finally:
        attacker_store.close()
        target_store.close()


@pytest.mark.asyncio
async def test_unsealed_client_selected_commitment_fails_before_provider_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Accept only the preparation service's inseparable source/commitment pair."""
    store = initialize_minio_store(private_prefix="negative/unsealed")

    @asynccontextmanager
    async def unexpected_client() -> Any:
        raise AssertionError("provider I/O occurred for an unsealed source")
        yield

    monkeypatch.setattr(store, "_client", unexpected_client)
    try:
        with pytest.raises(ArtifactInputMismatchError, match="not sealed"):
            await store.put(object())  # type: ignore[arg-type]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_hard_size_limit_fails_before_provider_io(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reject an over-limit commitment before opening an S3 client."""
    store = initialize_minio_store(private_prefix="negative/oversized")

    @asynccontextmanager
    async def unexpected_client() -> Any:
        raise AssertionError("provider I/O occurred for an oversized source")
        yield

    monkeypatch.setattr(store, "_client", unexpected_client)
    monkeypatch.setattr(s3_module, "HARD_MAXIMUM_ARTIFACT_BYTES", 1)
    try:
        async with minted_source(tmp_path / "scratch", b"12") as source:
            with pytest.raises(s3_module.ArtifactLimitExceededError):
                await store.put(source)
    finally:
        store.close()


def test_namespace_claim_mismatch_fails_before_provider_io() -> None:
    """Reject a configured namespace mismatch without routing elsewhere."""
    bootstrap = create_artifact_store_bootstrap(
        minio_settings(private_prefix="namespace/exact")
    )
    namespace = bootstrap.namespace_identity
    wrong = ArtifactStoreNamespaceClaim(
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace,
        namespace_fingerprint="sha256:" + "0" * 64,
    )
    with pytest.raises(ArtifactConfigurationError, match="does not match"):
        bootstrap.initialize_after_namespace_claim(wrong)


async def raw_minio_put(key: str, content: bytes) -> None:
    """Publish adversarial integration bytes outside the Workstream adapter."""
    session = AioSession()
    session.set_credentials(MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    async with session.create_client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        region_name=MINIO_REGION,
        config=AioConfig(s3={"addressing_style": "path"}),
    ) as client:
        await client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=content)


def test_s3_constructor_and_bootstrap_reject_invalid_runtime_values() -> None:
    """Fail closed on malformed direct construction outside validated settings."""
    session = AioSession()
    values = {
        "provider_profile": "minio",
        "region": MINIO_REGION,
        "endpoint_url": MINIO_ENDPOINT,
        "bucket": MINIO_BUCKET,
        "private_prefix": "negative/constructor",
        "addressing_style": "path",
        "session": session,
        "buffer_bytes": 2,
        "connect_timeout_seconds": 1,
        "read_timeout_seconds": 1,
        "write_timeout_seconds": 1,
        "pool_timeout_seconds": 1,
        "operation_total_timeout_seconds": 2,
        "max_pool_connections": 1,
    }
    for override in (
        {"provider_profile": "unknown"},
        {"session": object()},
        {"buffer_bytes": 0},
        {"buffer_bytes": True},
        {"max_pool_connections": 0},
        {"max_pool_connections": True},
        {"connect_timeout_seconds": 0},
        {"read_timeout_seconds": True},
    ):
        with pytest.raises(ArtifactConfigurationError):
            S3CompatibleArtifactStore(**(values | override))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        S3CompatibleArtifactStoreBootstrap(object())  # type: ignore[arg-type]


def test_namespace_claim_is_single_use_and_close_disables_operations() -> None:
    """One exact claim activates one adapter once and close revokes local use."""
    bootstrap = create_artifact_store_bootstrap(
        minio_settings(private_prefix="negative/single-use")
    )
    namespace = bootstrap.namespace_identity
    _, fingerprint = artifact_store_namespace_material(
        backend="s3_compatible",
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace,
    )
    claim = ArtifactStoreNamespaceClaim(bootstrap.identity, namespace, fingerprint)
    store = bootstrap.initialize_after_namespace_claim(claim)
    with pytest.raises(ArtifactConfigurationError, match="already initialized"):
        bootstrap.initialize_after_namespace_claim(claim)
    with pytest.raises(ArtifactConfigurationError, match="not initialized"):
        store.open("sha256/00/" + "0" * 62)


@pytest.mark.asyncio
async def test_invalid_provider_reference_and_range_fail_before_provider_io() -> None:
    """Reject caller-selected keys and malformed ranges at the adapter boundary."""
    store = initialize_minio_store(private_prefix="negative/references")
    try:
        with pytest.raises(ArtifactOperationConflictError):
            await store.head("customer/project/file")
        with pytest.raises(ArtifactOperationConflictError):
            store.open("sha256/00/" + "0" * 62, object())  # type: ignore[arg-type]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_head_maps_only_404_to_missing_and_rejects_invalid_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep denied access and malformed provider metadata distinct from absence."""
    store = initialize_minio_store(private_prefix="negative/head")
    provider_ref = "sha256/00/" + "0" * 62

    class Client:
        response: object

        async def head_object(self, **_kwargs: object) -> object:
            if isinstance(self.response, BaseException):
                raise self.response
            return self.response

    client = Client()

    @asynccontextmanager
    async def fake_client() -> Any:
        yield client

    monkeypatch.setattr(store, "_client", fake_client)
    try:
        client.response = _client_error("404", 404)
        assert (await store.head(provider_ref)).exists is False
        client.response = _client_error("AccessDenied", 403)
        with pytest.raises(ArtifactStoreUnavailableError):
            await store.head(provider_ref)
        client.response = _client_error("NoSuchKey", 403)
        with pytest.raises(ArtifactStoreUnavailableError):
            await store.head(provider_ref)
        client.response = {}
        with pytest.raises(ArtifactIntegrityError, match="exact size"):
            await store.head(provider_ref)
    finally:
        store.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("chunks", "expected_error"),
    [
        ([b"a", b""], "truncated"),
        ([b"abc"], "exceeded"),
        (["not-bytes"], "invalid bytes"),
    ],
)
async def test_open_rejects_invalid_provider_streams(
    monkeypatch: pytest.MonkeyPatch,
    chunks: list[object],
    expected_error: str,
) -> None:
    """Reject truncation, overread, and non-byte provider responses."""
    store = initialize_minio_store(private_prefix="negative/open")
    provider_ref = "sha256/00/" + "0" * 62

    class Body:
        def __init__(self) -> None:
            self._chunks = iter(chunks)

        async def __aenter__(self) -> Body:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def read(self, _amount: int) -> object:
            return next(self._chunks, b"")

    class Client:
        async def head_object(self, **_kwargs: object) -> dict[str, int]:
            return {"ContentLength": 2}

        async def get_object(self, **_kwargs: object) -> dict[str, object]:
            return {"Body": Body()}

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    monkeypatch.setattr(store, "_client", fake_client)
    try:
        with pytest.raises(ArtifactIntegrityError, match=expected_error):
            _ = [chunk async for chunk in store.open(provider_ref)]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_open_maps_provider_404_to_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Map an object disappearing between HEAD and GET to stable missing."""
    store = initialize_minio_store(private_prefix="negative/disappeared")
    provider_ref = "sha256/00/" + "0" * 62

    class Client:
        async def head_object(self, **_kwargs: object) -> dict[str, int]:
            return {"ContentLength": 1}

        async def get_object(self, **_kwargs: object) -> object:
            raise _client_error("NoSuchKey", 404)

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    monkeypatch.setattr(store, "_client", fake_client)
    try:
        with pytest.raises(ArtifactObjectMissingError):
            _ = [chunk async for chunk in store.open(provider_ref, ArtifactByteRange())]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_open_403_precedes_missing_like_provider_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Never turn denied reads into authoritative object absence."""
    store = initialize_minio_store(private_prefix="negative/denied-open")
    provider_ref = "sha256/00/" + "0" * 62

    class Client:
        async def head_object(self, **_kwargs: object) -> dict[str, int]:
            return {"ContentLength": 1}

        async def get_object(self, **_kwargs: object) -> object:
            raise _client_error("NoSuchKey", 403)

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    monkeypatch.setattr(store, "_client", fake_client)
    try:
        with pytest.raises(ArtifactStoreUnavailableError):
            _ = [chunk async for chunk in store.open(provider_ref)]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_precondition_failure_requires_exact_replay_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Never accept a conditional-write conflict without a complete read proof."""
    store = initialize_minio_store(private_prefix="negative/precondition")
    verified: list[str] = []

    class Client:
        async def put_object(self, **_kwargs: object) -> object:
            raise _client_error("PreconditionFailed", 412)

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    async def verify(provider_ref: str, _commitment: object) -> None:
        verified.append(provider_ref)

    monkeypatch.setattr(store, "_client", fake_client)
    monkeypatch.setattr(store, "_verify_exact", verify)
    try:
        async with minted_source(tmp_path / "scratch", b"replay") as source:
            result = await store.put(source)
        assert result.replayed is True
        assert verified == [result.provider_object_ref]
    finally:
        store.close()


@pytest.mark.asyncio
async def test_success_without_full_source_consumption_is_not_replay(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reject a success response when the SDK did not validate all source bytes."""
    store = initialize_minio_store(private_prefix="negative/unconsumed-success")

    class Client:
        async def put_object(self, **_kwargs: object) -> object:
            return {}

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    async def must_not_classify_as_replay(*_args: object) -> bool:
        raise AssertionError("unconsumed successful writes are not replay candidates")

    monkeypatch.setattr(store, "_client", fake_client)
    monkeypatch.setattr(store, "_matches_commitment", must_not_classify_as_replay)
    try:
        async with minted_source(tmp_path / "scratch", b"unconsumed") as source:
            with pytest.raises(
                ArtifactInputMismatchError,
                match="did not consume the sealed artifact source",
            ):
                await store.put(source)
    finally:
        store.close()


@pytest.mark.asyncio
async def test_nonprecondition_put_error_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Keep denied writes out of replay and integrity classifications."""
    store = initialize_minio_store(private_prefix="negative/denied-put")

    class Client:
        async def put_object(self, **_kwargs: object) -> object:
            raise _client_error("AccessDenied", 403)

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    monkeypatch.setattr(store, "_client", fake_client)
    try:
        async with minted_source(tmp_path / "scratch", b"denied") as source:
            with pytest.raises(ArtifactStoreUnavailableError):
                await store.put(source)
    finally:
        store.close()


@pytest.mark.asyncio
async def test_put_403_precedes_precondition_like_provider_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Never classify denied writes as replay candidates."""
    store = initialize_minio_store(private_prefix="negative/denied-precondition")

    class Client:
        async def put_object(self, **_kwargs: object) -> object:
            raise _client_error("PreconditionFailed", 403)

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    async def verification_must_not_run(*_args: object) -> None:
        raise AssertionError("denied writes cannot enter replay verification")

    monkeypatch.setattr(store, "_client", fake_client)
    monkeypatch.setattr(store, "_verify_exact", verification_must_not_run)
    try:
        async with minted_source(tmp_path / "scratch", b"denied") as source:
            with pytest.raises(ArtifactStoreUnavailableError):
                await store.put(source)
    finally:
        store.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("committed", [False, True])
async def test_uncertain_transport_put_requires_independent_observation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    committed: bool,
) -> None:
    """Resolve acknowledgement loss only from exact deterministic-key bytes."""
    store = initialize_minio_store(private_prefix=f"negative/uncertain/{committed}")
    observed: list[str] = []

    class Client:
        async def put_object(self, **_kwargs: object) -> object:
            raise OSError("connection closed")

    @asynccontextmanager
    async def fake_client() -> Any:
        yield Client()

    async def matches(provider_ref: str, _commitment: object) -> bool:
        observed.append(provider_ref)
        return committed

    monkeypatch.setattr(store, "_client", fake_client)
    monkeypatch.setattr(store, "_matches_commitment", matches)
    try:
        async with minted_source(tmp_path / "scratch", b"uncertain") as source:
            if committed:
                result = await store.put(source)
                assert result.replayed is True
                assert observed == [result.provider_object_ref]
            else:
                with pytest.raises(ArtifactStoreUnavailableError):
                    await store.put(source)
                assert len(observed) == 1
    finally:
        store.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("stored_bytes_match", [False, True])
async def test_uncertain_transport_put_uses_real_minio_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    stored_bytes_match: bool,
) -> None:
    """Classify acknowledgement loss only from the complete provider bytes."""
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:20]
    private_prefix = f"uncertain/real-observation/{nonce}"
    expected = b"exact committed bytes"
    digest = hashlib.sha256(expected).hexdigest()
    provider_ref = f"sha256/{digest[:2]}/{digest[2:]}"
    stored = expected if stored_bytes_match else b"wrong existing bytes"
    await raw_minio_put(f"{private_prefix}/{provider_ref}", stored)

    store = initialize_minio_store(private_prefix=private_prefix)
    original_client = store._client
    client_calls = 0

    class LostAcknowledgementClient:
        async def put_object(self, **_kwargs: object) -> object:
            raise OSError("connection closed after provider write")

    @asynccontextmanager
    async def lost_acknowledgement_then_real_provider() -> Any:
        nonlocal client_calls
        client_calls += 1
        if client_calls == 1:
            yield LostAcknowledgementClient()
            return
        async with original_client() as client:
            yield client

    monkeypatch.setattr(store, "_client", lost_acknowledgement_then_real_provider)
    try:
        async with minted_source(tmp_path / "scratch", expected) as source:
            if stored_bytes_match:
                result = await store.put(source)
                assert result.provider_object_ref == provider_ref
                assert result.replayed is True
            else:
                with pytest.raises(ArtifactIntegrityError):
                    await store.put(source)
        assert client_calls >= 3
    finally:
        store.close()


@pytest.mark.asyncio
async def test_put_observation_requires_canonical_commitment() -> None:
    """Reject caller-assembled observation requests before provider I/O."""
    store = initialize_minio_store(private_prefix="negative/observation")
    try:
        with pytest.raises(ArtifactOperationConflictError):
            await store.observe_put_result(object())  # type: ignore[arg-type]
    finally:
        store.close()


def _client_error(code: str, status: int) -> ClientError:
    """Build one sanitized provider error for adapter mapping tests."""
    return ClientError(
        {
            "Error": {"Code": code, "Message": "provider detail"},
            "ResponseMetadata": {"HTTPStatusCode": status},
        },
        "HeadObject",
    )
