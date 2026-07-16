"""PostgreSQL integration tests for the ArtifactStore v2 orchestration boundary."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.adapters.artifacts.local import LocalStorageAdapter
from app.core.config import Settings
from app.core.hashing import canonical_json_hash
from app.interfaces.artifacts import (
    ArtifactByteRange,
    ArtifactInputMismatchError,
    ArtifactObjectHead,
    ArtifactPutObservation,
    ArtifactPutResult,
    ArtifactStoreUnavailableError,
)
from app.interfaces.external_services import ExternalServiceAdapterIdentity
from app.modules.artifacts.models import (
    ArtifactContent,
    ArtifactOperationReceipt,
    ArtifactReplica,
    ArtifactStorageNamespace,
    ArtifactUploadItem,
    ArtifactUploadSession,
)
from app.modules.artifacts.preparation import (
    HARD_MAXIMUM_ARTIFACT_BYTES,
    ArtifactPreparationLimits,
    ArtifactPreparationService,
    ArtifactScratchManager,
)
from app.modules.artifacts.service import (
    ArtifactIngestStateError,
    ArtifactStorageNamespaceError,
    ArtifactStorageNamespaceSpec,
    ArtifactStorageOrchestrator,
    ProviderAttemptFence,
    artifact_storage_namespace_spec,
    validate_artifact_storage_namespace_at_startup,
)
import app.modules.artifacts.service as artifact_service_module
from app.modules.artifacts.sources import ArtifactCommitment, CommittedArtifactSource
from app.modules.projects.models import Project


def _alembic_config() -> Config:
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    return config


@pytest.fixture
def artifact_database_env(isolated_database_env: str, migration_lock) -> str:
    """Provide one fully migrated empty PostgreSQL database per test."""
    config = _alembic_config()
    with migration_lock():
        asyncio.run(_truncate_artifacts_if_present(isolated_database_env))
        command.downgrade(config, "base")
        command.upgrade(config, "head")
    yield isolated_database_env
    with migration_lock():
        asyncio.run(_truncate_artifacts(isolated_database_env))
        command.downgrade(config, "base")


async def _truncate_artifacts(database_url: str) -> None:
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "truncate table artifact_storage_namespaces, artifact_upload_sessions, "
                    "artifact_contents cascade"
                )
            )
    finally:
        await engine.dispose()


async def _truncate_artifacts_if_present(database_url: str) -> None:
    """Clear only artifact tables that exist at the database's current revision."""
    engine = create_async_engine(database_url)
    candidates = (
        "artifact_storage_namespaces",
        "artifact_upload_sessions",
        "artifact_contents",
    )
    try:
        async with engine.begin() as connection:
            existing = [
                table_name
                for table_name in candidates
                if await connection.scalar(
                    text("select to_regclass(:table_name) is not null"),
                    {"table_name": f"public.{table_name}"},
                )
            ]
            if existing:
                await connection.execute(text(f"truncate table {', '.join(existing)} cascade"))
    finally:
        await engine.dispose()


async def _byte_stream(*chunks: bytes) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk


def _preparation_limits() -> ArtifactPreparationLimits:
    return ArtifactPreparationLimits(
        aggregate_reserved_bytes=HARD_MAXIMUM_ARTIFACT_BYTES,
        maximum_files=2,
        maximum_concurrency=2,
        minimum_free_bytes=0,
        reservation_ttl_seconds=30,
        total_deadline_seconds=10,
        cleanup_margin_seconds=1,
        stream_buffer_bytes=2,
        maximum_source_bytes=1024,
    )


@asynccontextmanager
async def _minted_source(
    scratch_root: Path,
    content: bytes,
    *,
    media_type: str = "application/octet-stream",
) -> AsyncIterator[CommittedArtifactSource]:
    manager = ArtifactScratchManager(root=scratch_root, limits=_preparation_limits())
    prepared = await ArtifactPreparationService(manager).prepare(
        _byte_stream(content[:2], content[2:]),
        media_type=media_type,
    )
    try:
        async with prepared as source:
            yield source
    finally:
        manager.close()


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        environment="test",
        artifact_store_backend="local",
        artifact_local_root=tmp_path / "store",
        artifact_scratch_root=tmp_path / "scratch",
        artifact_scratch_minimum_free_bytes=0,
    )


async def _seed_reserved_item(
    session,
    commitment: ArtifactCommitment,
) -> str:
    project_id = str(uuid4())
    session_id = str(uuid4())
    item_id = str(uuid4())
    session.add(Project(id=project_id, name="Artifact project", slug=f"artifact-{project_id}"))
    await session.flush()
    session.add(
        ArtifactUploadSession(
            id=session_id,
            actor_id="actor-1",
            project_id=project_id,
            permitted_roles=["submission"],
            state="open",
            maximum_bytes=1024,
            current_bytes=0,
            reserved_bytes=commitment.byte_count,
            maximum_items=1,
            current_items=0,
            reserved_items=1,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            cas_version=0,
        )
    )
    await session.flush()
    session.add(
        ArtifactUploadItem(
            id=item_id,
            session_id=session_id,
            logical_role="submission",
            display_name="result.bin",
            media_type=commitment.media_type,
            reserved_bytes=commitment.byte_count,
            expected_sha256=commitment.sha256,
            expected_size=commitment.byte_count,
            idempotency_key=f"put-{item_id}",
            request_digest=canonical_json_hash(
                {
                    "sha256": commitment.sha256,
                    "byte_count": commitment.byte_count,
                    "media_type": commitment.media_type,
                }
            ),
            state="reserved",
            cas_version=0,
        )
    )
    await session.commit()
    return item_id


@pytest.mark.asyncio
async def test_put_acknowledgement_stops_at_pending_verification(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    content = b"artifact-v2"
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = LocalStorageAdapter(root=tmp_path / "store", buffer_bytes=2)
    try:
        async with _minted_source(tmp_path / "scratch", content) as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                namespace = artifact_storage_namespace_spec(_settings(tmp_path), store)
                result = await ArtifactStorageOrchestrator(
                    session, store, namespace
                ).put_reserved_item(item_id, source)
        async with _minted_source(tmp_path / "scratch-replay", content) as replay_source:
            async with factory() as session:
                replay_item_id = await _seed_reserved_item(
                    session, replay_source.commitment
                )
                replay = await ArtifactStorageOrchestrator(
                    session, store, namespace
                ).put_reserved_item(replay_item_id, replay_source)
                assert replay.replayed is True

        async with factory() as session:
            item = await session.get(ArtifactUploadItem, item_id)
            replica = (await session.execute(select(ArtifactReplica))).scalar_one()
            receipts = (await session.execute(select(ArtifactOperationReceipt))).scalars().all()
            receipt = next(value for value in receipts if value.upload_item_id == item_id)
            replay_receipt = next(
                value for value in receipts if value.upload_item_id == replay_item_id
            )
            namespace_row = (
                await session.execute(select(ArtifactStorageNamespace))
            ).scalar_one()
            assert item is not None
            assert item.state == "stored_pending_verification"
            assert item.provider_object_ref == result.provider_object_ref
            assert replica.verification_state == "pending"
            assert replica.availability_state == "unknown"
            assert replica.integrity_state == "unknown"
            assert replica.namespace_fingerprint == namespace_row.namespace_fingerprint
            assert receipt.operation == "put"
            assert receipt.outcome == "stored_pending_verification"
            assert receipt.provider_object_ref == result.provider_object_ref
            assert receipt.replayed is False
            assert len(receipts) == 2
            assert replay_receipt.replayed is True
            assert await store.head(result.provider_object_ref) == ArtifactObjectHead(
                result.provider_object_ref,
                exists=True,
                byte_count=len(content),
                    media_type=None,
            )
    finally:
        store.close()
        await engine.dispose()


class _UnavailableStore:
    """Count provider calls and fail with one sanitized retryable error."""

    identity = ExternalServiceAdapterIdentity("artifact_store", "local")

    def __init__(self) -> None:
        self.put_calls = 0

    async def put(self, _source: CommittedArtifactSource) -> ArtifactPutResult:
        self.put_calls += 1
        raise ArtifactStoreUnavailableError()

    async def observe_put_result(
        self, _commitment: ArtifactCommitment
    ) -> ArtifactPutObservation:
        raise NotImplementedError

    def open(
        self, _provider_object_ref: str, _byte_range: ArtifactByteRange | None = None
    ) -> AsyncIterator[bytes]:
        raise NotImplementedError

    async def head(self, _provider_object_ref: str) -> ArtifactObjectHead:
        raise NotImplementedError


class _TerminalStore(_UnavailableStore):
    async def put(self, _source: CommittedArtifactSource) -> ArtifactPutResult:
        self.put_calls += 1
        raise ArtifactInputMismatchError()


class _CancelledStore(_UnavailableStore):
    async def put(self, _source: CommittedArtifactSource) -> ArtifactPutResult:
        self.put_calls += 1
        raise asyncio.CancelledError("provider put cancelled")


class _AcknowledgingStore(_UnavailableStore):
    async def put(self, source: CommittedArtifactSource) -> ArtifactPutResult:
        self.put_calls += 1
        digest_hex = source.commitment.sha256[7:]
        return ArtifactPutResult(
            f"sha256/{digest_hex[:2]}/{digest_hex[2:]}",
            replayed=False,
        )


class _FinalizationCancelledOrchestrator(ArtifactStorageOrchestrator):
    async def _finalize_put(
        self,
        item_id: str,
        commitment: ArtifactCommitment,
        result: ArtifactPutResult,
        fence: ProviderAttemptFence,
        *,
        correlation_id: str,
    ) -> None:
        del item_id, commitment, result, fence, correlation_id
        raise asyncio.CancelledError("put finalization cancelled")


async def _assert_replay_required_without_durable_facts(
    factory: async_sessionmaker,
    item_id: str,
) -> None:
    async with factory() as session:
        item = await session.get(ArtifactUploadItem, item_id)
        assert item is not None
        upload_session = await session.get(ArtifactUploadSession, item.session_id)
        assert upload_session is not None
        assert item.state == "replay_required"
        assert item.error_code == "artifact_put_acknowledgement_unknown"
        assert upload_session.reserved_bytes == item.reserved_bytes
        assert upload_session.reserved_items == 1
        assert await session.scalar(select(ArtifactContent)) is None
        assert await session.scalar(select(ArtifactReplica)) is None
        assert await session.scalar(select(ArtifactOperationReceipt)) is None


@pytest.mark.asyncio
async def test_retryable_put_marks_existing_item_replay_required(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _UnavailableStore()
    try:
        async with _minted_source(tmp_path / "scratch", b"retry") as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                orchestrator = ArtifactStorageOrchestrator(
                    session,
                    store,
                    artifact_storage_namespace_spec(_settings(tmp_path), store),
                )
                with pytest.raises(ArtifactStoreUnavailableError):
                    await orchestrator.put_reserved_item(item_id, source)

        async with factory() as session:
            item = await session.get(ArtifactUploadItem, item_id)
            assert item is not None
            assert item.state == "replay_required"
            assert item.error_code == "artifact_put_acknowledgement_unknown"
            assert await session.scalar(select(ArtifactReplica)) is None
            assert await session.scalar(select(ArtifactOperationReceipt)) is None
        assert store.put_calls == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_provider_cancellation_persists_replay_required_without_facts(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _CancelledStore()
    try:
        async with _minted_source(tmp_path / "scratch", b"provider cancellation") as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                orchestrator = ArtifactStorageOrchestrator(
                    session,
                    store,
                    artifact_storage_namespace_spec(_settings(tmp_path), store),
                )
                with pytest.raises(asyncio.CancelledError, match="provider put cancelled"):
                    await orchestrator.put_reserved_item(item_id, source)

        await _assert_replay_required_without_durable_facts(factory, item_id)
        assert store.put_calls == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_finalization_cancellation_persists_replay_required_without_facts(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _AcknowledgingStore()
    try:
        async with _minted_source(tmp_path / "scratch", b"finalization cancellation") as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                orchestrator = _FinalizationCancelledOrchestrator(
                    session,
                    store,
                    artifact_storage_namespace_spec(_settings(tmp_path), store),
                )
                with pytest.raises(asyncio.CancelledError, match="finalization cancelled"):
                    await orchestrator.put_reserved_item(item_id, source)

        await _assert_replay_required_without_durable_facts(factory, item_id)
        assert store.put_calls == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_terminal_put_failure_releases_reservation_and_fails_item(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _TerminalStore()
    try:
        async with _minted_source(tmp_path / "scratch", b"terminal") as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                with pytest.raises(ArtifactInputMismatchError):
                    await ArtifactStorageOrchestrator(
                        session,
                        store,
                        artifact_storage_namespace_spec(_settings(tmp_path), store),
                    ).put_reserved_item(item_id, source)

        async with factory() as session:
            item = await session.get(ArtifactUploadItem, item_id)
            assert item is not None
            upload_session = await session.get(ArtifactUploadSession, item.session_id)
            assert item.state == "failed"
            assert item.error_code == "artifact_input_mismatch"
            assert upload_session is not None
            assert upload_session.reserved_bytes == 0
            assert upload_session.reserved_items == 0
        assert store.put_calls == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_changed_commitment_is_rejected_before_provider_io(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _UnavailableStore()
    try:
        async with _minted_source(tmp_path / "scratch-first", b"first") as first:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, first.commitment)
        async with _minted_source(tmp_path / "scratch-second", b"second") as second:
            async with factory() as session:
                with pytest.raises(ArtifactIngestStateError, match="commitment changed"):
                    await ArtifactStorageOrchestrator(
                        session,
                        store,
                        artifact_storage_namespace_spec(_settings(tmp_path), store),
                    ).put_reserved_item(item_id, second)
        assert store.put_calls == 0
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_namespace_mismatch_fails_before_provider_io(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _UnavailableStore()
    settings = _settings(tmp_path)
    canonical = artifact_storage_namespace_spec(settings, store)
    conflicting_descriptor = dict(canonical.namespace_descriptor)
    conflicting_descriptor["private_root_identity"] = "sha256:" + "f" * 64
    conflicting = ArtifactStorageNamespaceSpec(
        backend=canonical.backend,
        adapter=canonical.adapter,
        provider_profile=canonical.provider_profile,
        namespace_descriptor=conflicting_descriptor,
        namespace_fingerprint=canonical_json_hash(conflicting_descriptor),
    )
    try:
        async with factory() as session:
            await ArtifactStorageOrchestrator(
                session, store, canonical
            ).ensure_storage_namespace()
        async with _minted_source(tmp_path / "scratch", b"blocked") as source:
            async with factory() as session:
                item_id = await _seed_reserved_item(session, source.commitment)
                with pytest.raises(ArtifactStorageNamespaceError):
                    await ArtifactStorageOrchestrator(
                        session, store, conflicting
                    ).put_reserved_item(item_id, source)
        assert store.put_calls == 0
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_concurrent_different_first_namespace_writers_have_one_winner(
    artifact_database_env: str,
    tmp_path: Path,
) -> None:
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    store = _UnavailableStore()
    first = artifact_storage_namespace_spec(_settings(tmp_path), store)
    second_descriptor = dict(first.namespace_descriptor)
    second_descriptor["private_root_identity"] = "sha256:" + "a" * 64
    second = ArtifactStorageNamespaceSpec(
        backend=first.backend,
        adapter=first.adapter,
        provider_profile=first.provider_profile,
        namespace_descriptor=second_descriptor,
        namespace_fingerprint=canonical_json_hash(second_descriptor),
    )

    async def claim(spec: ArtifactStorageNamespaceSpec) -> object:
        async with factory() as session:
            try:
                return await ArtifactStorageOrchestrator(
                    session, store, spec
                ).ensure_storage_namespace()
            except ArtifactStorageNamespaceError as exc:
                return exc

    try:
        outcomes = await asyncio.gather(claim(first), claim(second))
        assert sum(isinstance(value, ArtifactStorageNamespace) for value in outcomes) == 1
        assert sum(isinstance(value, ArtifactStorageNamespaceError) for value in outcomes) == 1
        async with factory() as session:
            assert await session.scalar(select(ArtifactStorageNamespace)) is not None
    finally:
        await engine.dispose()


def test_namespace_descriptor_is_canonical_and_does_not_store_local_path(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    store = _UnavailableStore()
    spec = artifact_storage_namespace_spec(settings, store)
    serialized = repr(spec.namespace_descriptor)

    assert spec.backend == "local"
    assert spec.provider_profile == "local-v2"
    assert spec.namespace_fingerprint == canonical_json_hash(spec.namespace_descriptor)
    assert str(settings.artifact_local_root) not in serialized
    assert spec.namespace_descriptor["private_root_identity"] == canonical_json_hash(
        {"private_root": str(settings.artifact_local_root.resolve(strict=False))}
    )


def test_namespace_spec_rejects_adapter_drift_and_nonlocal_profile(tmp_path: Path) -> None:
    local_store = _UnavailableStore()
    with pytest.raises(ArtifactStorageNamespaceError, match="identity"):
        artifact_storage_namespace_spec(Settings(), local_store)

    class _S3Store(_UnavailableStore):
        identity = ExternalServiceAdapterIdentity("artifact_store", "s3_compatible")

    s3_settings = Settings(
        environment="test",
        artifact_store_backend="s3_compatible",
        artifact_scratch_root=tmp_path / "scratch",
    )
    with pytest.raises(ArtifactStorageNamespaceError, match="profile"):
        artifact_storage_namespace_spec(s3_settings, _S3Store())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider_failure",
    [asyncio.CancelledError("cancelled"), RuntimeError("provider crashed")],
)
async def test_unexpected_or_cancelled_provider_failure_requires_replay(
    tmp_path: Path,
    provider_failure: BaseException,
) -> None:
    store = _UnavailableStore()
    store.put = AsyncMock(side_effect=provider_failure)  # type: ignore[method-assign]
    orchestrator = ArtifactStorageOrchestrator(
        None,  # type: ignore[arg-type]
        store,
        artifact_storage_namespace_spec(_settings(tmp_path), store),
    )
    orchestrator._start_put = AsyncMock(  # type: ignore[method-assign]
        return_value=ProviderAttemptFence(1, 1)
    )
    orchestrator._mark_replay_required = AsyncMock()  # type: ignore[method-assign]

    async with _minted_source(tmp_path / "scratch", b"provider") as source:
        with pytest.raises(type(provider_failure)):
            await orchestrator.put_reserved_item("item", source)
    orchestrator._mark_replay_required.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "finalization_failure",
    [
        ArtifactInputMismatchError("mismatch"),
        asyncio.CancelledError("cancelled"),
        RuntimeError("database unavailable"),
    ],
)
async def test_finalization_failure_never_leaves_uploading_unresolved(
    tmp_path: Path,
    finalization_failure: BaseException,
) -> None:
    store = _UnavailableStore()
    store.put = AsyncMock(  # type: ignore[method-assign]
        return_value=ArtifactPutResult("sha256/00/" + "0" * 62, replayed=False)
    )
    orchestrator = ArtifactStorageOrchestrator(
        None,  # type: ignore[arg-type]
        store,
        artifact_storage_namespace_spec(_settings(tmp_path), store),
    )
    orchestrator._start_put = AsyncMock(  # type: ignore[method-assign]
        return_value=ProviderAttemptFence(1, 1)
    )
    orchestrator._finalize_put = AsyncMock(  # type: ignore[method-assign]
        side_effect=finalization_failure
    )
    orchestrator._fail_put = AsyncMock()  # type: ignore[method-assign]
    orchestrator._mark_replay_required = AsyncMock()  # type: ignore[method-assign]

    async with _minted_source(tmp_path / "scratch", b"finalize") as source:
        with pytest.raises(type(finalization_failure)):
            await orchestrator.put_reserved_item("item", source)
    if isinstance(finalization_failure, ArtifactInputMismatchError):
        orchestrator._fail_put.assert_awaited_once()  # type: ignore[attr-defined]
    else:
        orchestrator._mark_replay_required.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_startup_namespace_validation_uses_canonical_session_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _settings(tmp_path)
    store = _UnavailableStore()
    session = object()

    class _SessionContext:
        async def __aenter__(self) -> object:
            return session

        async def __aexit__(self, *_args: object) -> None:
            return None

    ensured = AsyncMock()

    class _Orchestrator:
        def __init__(self, candidate_session: object, candidate_store: object, spec: object) -> None:
            assert candidate_session is session
            assert candidate_store is store
            assert isinstance(spec, ArtifactStorageNamespaceSpec)

        ensure_storage_namespace = ensured

    monkeypatch.setattr(
        artifact_service_module,
        "get_session_factory",
        lambda: lambda: _SessionContext(),
    )
    monkeypatch.setattr(artifact_service_module, "ArtifactStorageOrchestrator", _Orchestrator)

    await validate_artifact_storage_namespace_at_startup(store, settings)
    ensured.assert_awaited_once()


def test_models_remove_v1_provider_retention_and_receipt_fields() -> None:
    assert not hasattr(ArtifactReplica, "retention_state")
    assert not hasattr(ArtifactReplica, "provider_artifact_id")
    assert not hasattr(ArtifactOperationReceipt, "provider_receipt_id")
    assert not hasattr(ArtifactOperationReceipt, "retention_reference")
    assert not hasattr(ArtifactOperationReceipt, "service_principal")
    assert not hasattr(ArtifactUploadItem, "provider_operation_reference")
    assert hasattr(ArtifactReplica, "provider_object_ref")
    assert hasattr(ArtifactStorageNamespace, "namespace_fingerprint")
