"""Database operations for artifact ingest and immutable facts."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.artifacts.models import (
    ArtifactContent,
    ArtifactOperationReceipt,
    ArtifactReplica,
    ArtifactUploadItem,
    ArtifactUploadSession,
)


class ArtifactRepository:
    """Persist artifact state transitions under caller-owned transactions."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to one async database session."""
        self._session = session

    async def lock_upload_item(self, item_id: str) -> ArtifactUploadItem | None:
        """Load one upload item with a row lock."""
        result = await self._session.execute(
            select(ArtifactUploadItem)
            .where(ArtifactUploadItem.id == item_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def lock_upload_session(self, session_id: str) -> ArtifactUploadSession | None:
        """Load one upload session with a row lock."""
        result = await self._session.execute(
            select(ArtifactUploadSession)
            .where(ArtifactUploadSession.id == session_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_or_create_content(self, content: ArtifactContent) -> ArtifactContent:
        """Return the immutable content fact for one digest and size."""
        await self._session.execute(
            insert(ArtifactContent)
            .values(
                id=content.id,
                sha256=content.sha256,
                byte_count=content.byte_count,
                media_type=content.media_type,
                normalized_display_name=content.normalized_display_name,
            )
            .on_conflict_do_nothing(constraint="uq_artifact_content_digest_size")
        )
        result = await self._session.execute(
            select(ArtifactContent).where(
                ArtifactContent.sha256 == content.sha256,
                ArtifactContent.byte_count == content.byte_count,
            )
        )
        return result.scalar_one()

    async def add_replica(self, replica: ArtifactReplica) -> ArtifactReplica:
        """Persist a provider replica observation."""
        self._session.add(replica)
        await self._session.flush()
        return replica

    async def add_receipt(self, receipt: ArtifactOperationReceipt) -> ArtifactOperationReceipt:
        """Persist one append-only provider operation receipt."""
        self._session.add(receipt)
        await self._session.flush()
        return receipt

    async def get_receipt(
        self,
        adapter: str,
        service_principal: str,
        operation: str,
        idempotency_key: str,
    ) -> ArtifactOperationReceipt | None:
        """Load the authoritative Workstream receipt for one operation identity."""
        result = await self._session.execute(
            select(ArtifactOperationReceipt).where(
                ArtifactOperationReceipt.adapter == adapter,
                ArtifactOperationReceipt.service_principal == service_principal,
                ArtifactOperationReceipt.operation == operation,
                ArtifactOperationReceipt.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def get_replica_by_provider_id(
        self, adapter: str, provider_artifact_id: str
    ) -> ArtifactReplica | None:
        """Load one provider replica by its opaque provider identifier."""
        result = await self._session.execute(
            select(ArtifactReplica).where(
                ArtifactReplica.adapter == adapter,
                ArtifactReplica.provider_artifact_id == provider_artifact_id,
            )
        )
        return result.scalar_one_or_none()

    async def lock_replica_by_provider_id(
        self, adapter: str, provider_artifact_id: str
    ) -> ArtifactReplica | None:
        """Load one provider replica under a reconciliation row lock."""
        result = await self._session.execute(
            select(ArtifactReplica)
            .where(
                ArtifactReplica.adapter == adapter,
                ArtifactReplica.provider_artifact_id == provider_artifact_id,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()
