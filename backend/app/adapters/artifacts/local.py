"""Private local implementation of the immutable ArtifactStore v2 port."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import contextmanager
import errno
import fcntl
import hashlib
import math
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterator
from uuid import uuid4

from app.core.cancellation import (
    await_cancellation_resistant,
    run_blocking_cancellation_resistant,
)
from app.core.file_locks import acquire_exclusive_file_lock
from app.interfaces.artifacts import (
    ArtifactByteRange,
    ArtifactConfigurationError,
    ArtifactInputMismatchError,
    ArtifactIntegrityError,
    ArtifactLimitExceededError,
    ArtifactObjectHead,
    ArtifactObjectMissingError,
    ArtifactOperationConflictError,
    ArtifactPutObservation,
    ArtifactPutResult,
    ArtifactRangeInvalidError,
    ArtifactStoreError,
    ArtifactStoreUnavailableError,
)
from app.interfaces.external_services import ExternalServiceAdapterIdentity
from app.modules.artifacts.preparation import HARD_MAXIMUM_ARTIFACT_BYTES
from app.modules.artifacts.sources import ArtifactCommitment, CommittedArtifactSource


_IDENTITY = ExternalServiceAdapterIdentity("artifact_store", "local")
_LAYOUT_MARKER = ".workstream-artifact-store-v2"
_LAYOUT_MARKER_BYTES = b"workstream-artifact-store-v2\n"
_PROVIDER_OBJECT_REF = re.compile(r"^sha256/([0-9a-f]{2})/([0-9a-f]{62})$")
_TEMPORARY_NAME = re.compile(r"^\.put\.[0-9a-f]{32}\.tmp$")


class LocalStorageAdapter:
    """Filesystem-backed immutable byte provider for development and tests."""

    def __init__(
        self,
        *,
        root: Path,
        buffer_bytes: int = 1024 * 1024,
        lock_timeout_seconds: float = 1800.0,
    ) -> None:
        """Create or validate one private v2-only local storage root."""
        if type(buffer_bytes) is not int or not 1 <= buffer_bytes <= 1024 * 1024:
            raise ValueError("artifact buffer must be between 1 byte and 1 MiB")
        if (
            isinstance(lock_timeout_seconds, bool)
            or not isinstance(lock_timeout_seconds, (int, float))
            or not math.isfinite(lock_timeout_seconds)
            or lock_timeout_seconds <= 0
        ):
            raise ValueError("artifact lock timeout is invalid")

        self._buffer_bytes = buffer_bytes
        self._lock_timeout_seconds = float(lock_timeout_seconds)
        self._root_fd = -1
        self._sha256_fd = -1
        self._tmp_fd = -1
        self._locks_fd = -1
        try:
            self._initialize_root(root)
        except (ArtifactConfigurationError, ValueError):
            self.close()
            raise
        except OSError:
            self.close()
            raise ArtifactConfigurationError("local artifact storage is unavailable") from None

    @property
    def identity(self) -> ExternalServiceAdapterIdentity:
        """Return the canonical artifact-store/local adapter identity."""
        return _IDENTITY

    def close(self) -> None:
        """Release pinned private directory descriptors."""
        for attribute in ("_locks_fd", "_tmp_fd", "_sha256_fd", "_root_fd"):
            descriptor = getattr(self, attribute, -1)
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                setattr(self, attribute, -1)

    def __del__(self) -> None:
        """Best-effort descriptor cleanup."""
        self.close()

    async def put(self, source: CommittedArtifactSource) -> ArtifactPutResult:
        """Publish sealed bytes exclusively or verify an exact immutable replay."""
        if type(source) is not CommittedArtifactSource:
            raise ArtifactInputMismatchError("artifact source is not sealed")
        commitment = source.commitment
        if commitment.byte_count > HARD_MAXIMUM_ARTIFACT_BYTES:
            raise ArtifactLimitExceededError("artifact source exceeds provider limit")

        provider_object_ref = self._provider_object_ref(commitment)
        lock: tuple[Any, int] | None = None
        descriptor: int | None = None
        temporary_name: str | None = None
        try:
            lock = await self._acquire_lock_async(commitment.sha256[7:])
            try:
                await self._run_io(self._head_object, provider_object_ref)
            except FileNotFoundError:
                pass
            else:
                await self._run_io(
                    self._verify_exact_under_lock,
                    provider_object_ref,
                    commitment,
                )
                return ArtifactPutResult(provider_object_ref, replayed=True)

            descriptor, temporary_name = await self._create_temporary_async()
            digest = hashlib.sha256()
            byte_count = 0
            async for source_chunk in source.stream():
                if not isinstance(source_chunk, bytes):
                    raise ArtifactInputMismatchError("artifact source must yield bytes")
                view = memoryview(source_chunk)
                for offset in range(0, len(view), self._buffer_bytes):
                    chunk = view[offset : offset + self._buffer_bytes]
                    byte_count += len(chunk)
                    if byte_count > commitment.byte_count:
                        raise ArtifactInputMismatchError(
                            "artifact source exceeds committed byte count"
                        )
                    digest.update(chunk)
                    await self._run_io(self._write_all, descriptor, chunk)

            observed_sha256 = f"sha256:{digest.hexdigest()}"
            if (
                byte_count != commitment.byte_count
                or observed_sha256 != commitment.sha256
            ):
                raise ArtifactInputMismatchError("artifact source violates commitment")

            await self._run_io(self._seal_temporary, descriptor)
            published = await self._run_io(
                self._publish_exclusive,
                temporary_name,
                provider_object_ref,
            )
            temporary_name = None
            if not published:
                await self._run_io(
                    self._verify_exact_under_lock,
                    provider_object_ref,
                    commitment,
                )
                return ArtifactPutResult(provider_object_ref, replayed=True)
            return ArtifactPutResult(provider_object_ref, replayed=False)
        except asyncio.CancelledError as cancellation:
            await await_cancellation_resistant(
                asyncio.to_thread(self._cleanup_resources, descriptor, temporary_name, lock)
            )
            descriptor = None
            temporary_name = None
            lock = None
            raise cancellation
        except ArtifactStoreError:
            raise
        except OSError:
            raise ArtifactStoreUnavailableError("local artifact operation failed") from None
        finally:
            if descriptor is not None or temporary_name is not None or lock is not None:
                await self._run_io(
                    self._cleanup_resources,
                    descriptor,
                    temporary_name,
                    lock,
                )

    async def observe_put_result(
        self,
        commitment: ArtifactCommitment,
    ) -> ArtifactPutObservation:
        """Read and validate the complete deterministic object when it exists."""
        if type(commitment) is not ArtifactCommitment:
            raise ArtifactOperationConflictError("artifact commitment is invalid")
        provider_object_ref = self._provider_object_ref(commitment)
        observed = await self.head(provider_object_ref)
        if not observed.exists:
            return ArtifactPutObservation(provider_object_ref, committed=False)
        await self._verify_exact(provider_object_ref, commitment)
        return ArtifactPutObservation(provider_object_ref, committed=True)

    def open(
        self,
        provider_object_ref: str,
        byte_range: ArtifactByteRange | None = None,
    ) -> AsyncIterator[bytes]:
        """Stream a full object or range through bounded off-loop reads."""
        self._parse_provider_object_ref(provider_object_ref)
        if byte_range is not None and type(byte_range) is not ArtifactByteRange:
            raise ArtifactOperationConflictError("artifact byte range is invalid")
        selected_range = byte_range or ArtifactByteRange()

        async def iterate() -> AsyncIterator[bytes]:
            """Yield bounded chunks while retaining one validated descriptor."""
            descriptor: int | None = None
            try:
                try:
                    descriptor, byte_count = await self._open_object_async(
                        provider_object_ref
                    )
                except FileNotFoundError:
                    raise ArtifactObjectMissingError("artifact object is missing") from None
                if selected_range.offset > byte_count:
                    raise ArtifactRangeInvalidError("artifact range starts past object end")
                remaining = byte_count - selected_range.offset
                if selected_range.length is not None:
                    remaining = min(remaining, selected_range.length)
                position = selected_range.offset
                while remaining:
                    chunk = await self._run_io(
                        os.pread,
                        descriptor,
                        min(self._buffer_bytes, remaining),
                        position,
                    )
                    if not chunk:
                        raise ArtifactIntegrityError("artifact object was truncated")
                    if len(chunk) > self._buffer_bytes or len(chunk) > remaining:
                        raise ArtifactIntegrityError("artifact read exceeded its bound")
                    position += len(chunk)
                    remaining -= len(chunk)
                    yield chunk
            except asyncio.CancelledError as cancellation:
                if descriptor is not None:
                    await await_cancellation_resistant(asyncio.to_thread(os.close, descriptor))
                    descriptor = None
                raise cancellation
            except ArtifactStoreError:
                raise
            except OSError:
                raise ArtifactStoreUnavailableError("local artifact read failed") from None
            finally:
                if descriptor is not None:
                    await self._run_io(os.close, descriptor)

        return iterate()

    async def head(self, provider_object_ref: str) -> ArtifactObjectHead:
        """Return an existing or missing observation without exposing paths."""
        self._parse_provider_object_ref(provider_object_ref)
        try:
            try:
                byte_count = await self._run_io(
                    self._head_object_with_recovery,
                    provider_object_ref,
                )
            except FileNotFoundError:
                return ArtifactObjectHead(provider_object_ref, exists=False)
            return ArtifactObjectHead(
                provider_object_ref,
                exists=True,
                byte_count=byte_count,
            )
        except ArtifactStoreError:
            raise
        except OSError:
            raise ArtifactStoreUnavailableError("local artifact head failed") from None

    async def _verify_exact(
        self,
        provider_object_ref: str,
        commitment: ArtifactCommitment,
    ) -> None:
        """Independently hash and count one complete existing object."""
        digest = hashlib.sha256()
        byte_count = 0
        async for chunk in self.open(provider_object_ref):
            digest.update(chunk)
            byte_count += len(chunk)
        if (
            byte_count != commitment.byte_count
            or f"sha256:{digest.hexdigest()}" != commitment.sha256
        ):
            raise ArtifactIntegrityError("artifact object violates commitment")

    async def _run_io(self, function: Any, *args: Any) -> Any:
        """Complete blocking filesystem work before preserving cancellation."""
        return await run_blocking_cancellation_resistant(function, *args)

    async def _acquire_lock_async(self, digest_hex: str) -> tuple[Any, int]:
        """Acquire a cross-process digest lock without leaking it on cancellation."""
        task = asyncio.create_task(asyncio.to_thread(self._acquire_lock, digest_hex))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError as cancellation:
            try:
                lock = await await_cancellation_resistant(task)
            except Exception:
                raise cancellation from None
            await await_cancellation_resistant(asyncio.to_thread(self._release_lock, lock))
            raise cancellation

    async def _create_temporary_async(self) -> tuple[int, str]:
        """Create a temporary file without losing ownership on cancellation."""
        task = asyncio.create_task(asyncio.to_thread(self._create_temporary))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError as cancellation:
            try:
                descriptor, temporary_name = await await_cancellation_resistant(task)
            except Exception:
                raise cancellation from None
            await await_cancellation_resistant(
                asyncio.to_thread(
                    self._cleanup_resources,
                    descriptor,
                    temporary_name,
                    None,
                )
            )
            raise cancellation

    async def _open_object_async(self, provider_object_ref: str) -> tuple[int, int]:
        """Open an object without losing descriptor ownership on cancellation."""
        task = asyncio.create_task(
            asyncio.to_thread(self._open_object_with_recovery, provider_object_ref)
        )
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError as cancellation:
            try:
                descriptor, _ = await await_cancellation_resistant(task)
            except Exception:
                raise cancellation from None
            await await_cancellation_resistant(asyncio.to_thread(os.close, descriptor))
            raise cancellation

    def _initialize_root(self, configured_root: Path) -> None:
        """Initialize only an empty or already-valid v2 private root."""
        if not isinstance(configured_root, Path):
            raise ValueError("artifact root must be a path")
        if configured_root.is_symlink():
            raise ArtifactConfigurationError("local artifact root is unsafe")
        configured_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._root_fd = os.open(
            configured_root,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        self._assert_private_directory(self._root_fd)

        entries = set(os.listdir(self._root_fd))
        if _LAYOUT_MARKER not in entries:
            if entries:
                raise ArtifactConfigurationError("local artifact layout is incompatible")
            try:
                marker = os.open(
                    _LAYOUT_MARKER,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                    dir_fd=self._root_fd,
                )
            except FileExistsError:
                pass
            else:
                try:
                    self._write_all(marker, memoryview(_LAYOUT_MARKER_BYTES))
                    os.fsync(marker)
                finally:
                    os.close(marker)
                os.fsync(self._root_fd)
        self._validate_marker()

        objects_fd = self._ensure_directory(self._root_fd, "objects")
        try:
            self._sha256_fd = self._ensure_directory(objects_fd, "sha256")
        finally:
            os.close(objects_fd)
        self._tmp_fd = self._ensure_directory(self._root_fd, "tmp")
        self._locks_fd = self._ensure_directory(self._root_fd, "locks")

    def _validate_marker(self) -> None:
        """Require the exact private v2 layout marker."""
        descriptor = os.open(
            _LAYOUT_MARKER,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=self._root_fd,
        )
        try:
            self._assert_private_regular(descriptor)
            content = os.read(descriptor, len(_LAYOUT_MARKER_BYTES) + 1)
            if content != _LAYOUT_MARKER_BYTES:
                raise ArtifactConfigurationError("local artifact layout is incompatible")
        finally:
            os.close(descriptor)

    def _ensure_directory(self, parent_fd: int, name: str) -> int:
        """Create or open one fixed private no-follow directory."""
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        self._assert_private_directory(descriptor)
        return descriptor

    def _provider_object_ref(self, commitment: ArtifactCommitment) -> str:
        """Derive one identity-free object reference from canonical SHA-256."""
        digest_hex = commitment.sha256[7:]
        return f"sha256/{digest_hex[:2]}/{digest_hex[2:]}"

    @staticmethod
    def _parse_provider_object_ref(provider_object_ref: str) -> tuple[str, str]:
        """Validate the exact opaque local provider-reference grammar."""
        if not isinstance(provider_object_ref, str):
            raise ArtifactOperationConflictError("artifact provider reference is invalid")
        match = _PROVIDER_OBJECT_REF.fullmatch(provider_object_ref)
        if match is None:
            raise ArtifactOperationConflictError("artifact provider reference is invalid")
        return match.group(1), match.group(2)

    def _open_prefix(self, prefix: str, *, create: bool) -> int:
        """Open one digest-prefix directory without following links."""
        if create:
            try:
                os.mkdir(prefix, 0o700, dir_fd=self._sha256_fd)
            except FileExistsError:
                pass
        try:
            descriptor = os.open(
                prefix,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=self._sha256_fd,
            )
        except OSError as exc:
            if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise ArtifactIntegrityError("local artifact prefix is unsafe") from None
            raise
        self._assert_private_directory(descriptor)
        if create:
            os.fsync(self._sha256_fd)
        return descriptor

    def _create_temporary(self) -> tuple[int, str]:
        """Create one unpublished private temporary object."""
        name = f".put.{uuid4().hex}.tmp"
        descriptor = os.open(
            name,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=self._tmp_fd,
        )
        self._assert_private_regular(descriptor)
        return descriptor, name

    @staticmethod
    def _seal_temporary(descriptor: int) -> None:
        """Make one complete temporary object read-only and durable."""
        os.fchmod(descriptor, 0o400)
        os.fsync(descriptor)

    def _publish_exclusive(self, temporary_name: str, provider_object_ref: str) -> bool:
        """Hard-link one complete object without ever replacing existing bytes."""
        prefix, filename = self._parse_provider_object_ref(provider_object_ref)
        prefix_fd = self._open_prefix(prefix, create=True)
        try:
            try:
                os.link(
                    temporary_name,
                    filename,
                    src_dir_fd=self._tmp_fd,
                    dst_dir_fd=prefix_fd,
                    follow_symlinks=False,
                )
            except FileExistsError:
                os.unlink(temporary_name, dir_fd=self._tmp_fd)
                os.fsync(self._tmp_fd)
                return False
            os.fsync(prefix_fd)
            os.unlink(temporary_name, dir_fd=self._tmp_fd)
            os.fsync(self._tmp_fd)
            return True
        finally:
            os.close(prefix_fd)

    def _head_object(self, provider_object_ref: str) -> int:
        """Return an exact size after validating one private regular object."""
        descriptor, byte_count = self._open_object(provider_object_ref)
        os.close(descriptor)
        return byte_count

    def _head_object_with_recovery(self, provider_object_ref: str) -> int:
        """Recover an interrupted publication under its digest lock before head."""
        prefix, filename = self._parse_provider_object_ref(provider_object_ref)
        with self._locked_file(prefix + filename):
            return self._head_object(provider_object_ref)

    def _open_object_with_recovery(self, provider_object_ref: str) -> tuple[int, int]:
        """Recover an interrupted publication under its digest lock before open."""
        prefix, filename = self._parse_provider_object_ref(provider_object_ref)
        with self._locked_file(prefix + filename):
            return self._open_object(provider_object_ref)

    def _open_object(self, provider_object_ref: str) -> tuple[int, int]:
        """Open one immutable no-follow object and return its exact size."""
        prefix, filename = self._parse_provider_object_ref(provider_object_ref)
        prefix_fd = self._open_prefix(prefix, create=False)
        descriptor = -1
        try:
            try:
                descriptor = os.open(
                    filename,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=prefix_fd,
                )
            except OSError as exc:
                if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                    raise ArtifactIntegrityError("local artifact object is unsafe") from None
                raise
            details = self._assert_recoverable_object(descriptor)
            if details.st_nlink == 2:
                self._recover_interrupted_publication(descriptor, details, prefix_fd)
                details = self._assert_private_regular(descriptor)
            if stat.S_IMODE(details.st_mode) != 0o400:
                raise ArtifactIntegrityError("local artifact object is mutable")
            return descriptor, details.st_size
        except BaseException:
            if descriptor >= 0:
                os.close(descriptor)
            raise
        finally:
            os.close(prefix_fd)

    def _recover_interrupted_publication(
        self,
        descriptor: int,
        object_stat: os.stat_result,
        prefix_fd: int,
    ) -> None:
        """Remove the one sealed temp hard link left by a crashed publisher."""
        matches: list[str] = []
        for name in os.listdir(self._tmp_fd):
            if _TEMPORARY_NAME.fullmatch(name) is None:
                continue
            try:
                candidate = os.stat(name, dir_fd=self._tmp_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            if candidate.st_dev == object_stat.st_dev and candidate.st_ino == object_stat.st_ino:
                if (
                    not stat.S_ISREG(candidate.st_mode)
                    or candidate.st_mode & 0o077
                    or stat.S_IMODE(candidate.st_mode) != 0o400
                    or candidate.st_nlink != 2
                ):
                    raise ArtifactIntegrityError("local artifact recovery link is unsafe")
                matches.append(name)
        if len(matches) != 1:
            raise ArtifactIntegrityError("local artifact publication is ambiguous")
        os.unlink(matches[0], dir_fd=self._tmp_fd)
        os.fsync(self._tmp_fd)
        os.fsync(prefix_fd)
        if os.fstat(descriptor).st_nlink != 1:
            raise ArtifactIntegrityError("local artifact publication recovery failed")

    def _verify_exact_under_lock(
        self,
        provider_object_ref: str,
        commitment: ArtifactCommitment,
    ) -> None:
        """Hash one object while the caller owns its digest lock."""
        descriptor, byte_count = self._open_object(provider_object_ref)
        digest = hashlib.sha256()
        observed_bytes = 0
        try:
            while observed_bytes < byte_count:
                chunk = os.read(descriptor, min(self._buffer_bytes, byte_count - observed_bytes))
                if not chunk:
                    raise ArtifactIntegrityError("artifact object was truncated")
                observed_bytes += len(chunk)
                digest.update(chunk)
        finally:
            os.close(descriptor)
        if (
            observed_bytes != commitment.byte_count
            or f"sha256:{digest.hexdigest()}" != commitment.sha256
        ):
            raise ArtifactIntegrityError("artifact object violates commitment")

    @contextmanager
    def _locked_file(self, digest_hex: str) -> Iterator[int]:
        """Own one bounded cross-process lock for a canonical digest."""
        descriptor = os.open(
            f"{digest_hex}.lock",
            os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=self._locks_fd,
        )
        try:
            self._assert_private_regular(descriptor)
            try:
                acquire_exclusive_file_lock(
                    descriptor,
                    timeout_seconds=self._lock_timeout_seconds,
                )
            except TimeoutError:
                raise ArtifactStoreUnavailableError(
                    "local artifact lock deadline exceeded"
                ) from None
            yield descriptor
        finally:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)

    def _acquire_lock(self, digest_hex: str) -> tuple[Any, int]:
        """Acquire one validated digest lock."""
        if re.fullmatch(r"[0-9a-f]{64}", digest_hex) is None:
            raise ArtifactOperationConflictError("artifact commitment is invalid")
        manager = self._locked_file(digest_hex)
        descriptor = manager.__enter__()
        return manager, descriptor

    @staticmethod
    def _release_lock(lock: tuple[Any, int]) -> None:
        """Release one owned digest lock."""
        manager, _ = lock
        manager.__exit__(None, None, None)

    def _cleanup_resources(
        self,
        descriptor: int | None,
        temporary_name: str | None,
        lock: tuple[Any, int] | None,
    ) -> None:
        """Release all private put resources after failure or cancellation."""
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary_name is not None and _TEMPORARY_NAME.fullmatch(temporary_name):
            try:
                os.unlink(temporary_name, dir_fd=self._tmp_fd)
                os.fsync(self._tmp_fd)
            except FileNotFoundError:
                pass
        if lock is not None:
            self._release_lock(lock)

    @staticmethod
    def _write_all(descriptor: int, chunk: memoryview) -> None:
        """Write one already-bounded view completely."""
        remaining = chunk
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError(errno.EIO, "short artifact write")
            remaining = remaining[written:]

    @staticmethod
    def _assert_private_directory(descriptor: int) -> os.stat_result:
        """Require one owner-private directory descriptor."""
        details = os.fstat(descriptor)
        if not stat.S_ISDIR(details.st_mode) or details.st_mode & 0o077:
            raise ArtifactConfigurationError("local artifact directory is unsafe")
        return details

    @staticmethod
    def _assert_private_regular(descriptor: int) -> os.stat_result:
        """Require one owner-private, single-link regular file."""
        details = os.fstat(descriptor)
        if (
            not stat.S_ISREG(details.st_mode)
            or details.st_mode & 0o077
            or details.st_nlink != 1
        ):
            raise ArtifactIntegrityError("local artifact object is unsafe")
        return details

    @staticmethod
    def _assert_recoverable_object(descriptor: int) -> os.stat_result:
        """Allow only the one extra link produced by interrupted publication."""
        details = os.fstat(descriptor)
        if (
            not stat.S_ISREG(details.st_mode)
            or details.st_mode & 0o077
            or details.st_nlink not in {1, 2}
        ):
            raise ArtifactIntegrityError("local artifact object is unsafe")
        return details
