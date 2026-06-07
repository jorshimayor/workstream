"""Service layer for task queue lifecycle and assignment operations."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_any_role
from app.modules.projects.models import (
    CheckerPolicy,
    PaymentPolicy,
    ProjectGuide,
    RevisionPolicy,
    ReviewPolicy,
)
from app.modules.projects.repository import ProjectRepository
from app.modules.tasks.lifecycle import (
    TASK_STATUS_CLAIMED,
    TASK_STATUS_DRAFT,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_READY,
    TASK_STATUS_SCREENING,
    InvalidTaskTransition,
    ensure_allowed_transition,
)
from app.modules.tasks.models import (
    AuditEvent,
    ReviewerProfile,
    TaskAssignment,
    WorkerProfile,
    WorkstreamTask,
)
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import (
    AssignmentResponse,
    AuditEventResponse,
    TaskCreate,
    TaskResponse,
    TaskWithAssignmentResponse,
)
from app.schemas.auth import ActorContext

PROJECT_OPERATOR_ROLES = {"admin", "project_manager"}
TASK_VIEW_ROLES = {"admin", "project_manager", "worker", "reviewer", "finance", "auditor"}
TASK_CLAIM_ROLES = {"worker"}
TASK_START_ROLES = {"admin", "project_manager", "worker"}
TASK_START_OPERATOR_ROLES = {"admin", "project_manager"}


class TaskServiceError(Exception):
    """Base error for task service failures mapped to API responses."""

    status_code = 400


class TaskNotFound(TaskServiceError):
    """Raised when a task id does not match a stored task."""

    status_code = 404


class TaskProjectNotReady(TaskServiceError):
    """Raised when a project does not have active guide and policy context."""

    status_code = 422


class TaskTransitionBlocked(TaskServiceError):
    """Raised when a task lifecycle transition is blocked by policy."""

    status_code = 409


class TaskValidationError(TaskServiceError):
    """Raised when a task is missing fields required by its guide."""

    status_code = 422


class TaskAssignmentConflict(TaskServiceError):
    """Raised when a task already has an active worker assignment."""

    status_code = 409


class WorkerProfileRequired(TaskServiceError):
    """Raised when a worker tries to claim without an active worker profile."""

    status_code = 403


class TaskService:
    """Coordinates task lifecycle rules, assignment, and audit writes."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a service instance bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current request.
        """
        self._session = session
        self._repo = TaskRepository(session)
        self._project_repo = ProjectRepository(session)

    async def create_task(
        self,
        actor: ActorContext,
        project_id: str,
        payload: TaskCreate,
    ) -> TaskResponse:
        """Create a draft task under a project.

        Args:
            actor: Verified Flow actor context for the current request.
            project_id: Project that owns the task.
            payload: Draft task fields.

        Returns:
            Created task response.

        Raises:
            PermissionDenied: If the actor cannot create tasks.
            TaskProjectNotReady: If the project id is unknown.
        """
        require_any_role(actor, PROJECT_OPERATOR_ROLES)
        project = await self._project_repo.get_project(project_id)
        if project is None:
            raise TaskProjectNotReady("project not found")

        task = WorkstreamTask(
            id=str(uuid4()),
            project_id=project_id,
            source_type=payload.source_type,
            source_ref=payload.source_ref,
            source_payload_hash=payload.source_payload_hash,
            import_batch_id=payload.import_batch_id,
            external_task_id=payload.external_task_id,
            title=payload.title,
            description=payload.description,
            task_type=payload.task_type,
            difficulty=payload.difficulty,
            skill_tags=payload.skill_tags,
            estimated_time_minutes=payload.estimated_time_minutes,
            status=TASK_STATUS_DRAFT,
            acceptance_criteria=payload.acceptance_criteria,
            rejection_criteria=payload.rejection_criteria,
            required_files=payload.required_files,
            required_evidence=payload.required_evidence,
            deadline_at=payload.deadline_at,
            created_by=actor.actor_id,
        )
        task = await self._repo.add_task(task)
        await self._write_task_audit(
            actor,
            task,
            event_type="task_created",
            from_status=None,
            to_status=TASK_STATUS_DRAFT,
            reason=None,
            event_payload={"source_type": task.source_type},
        )
        await self._session.commit()
        await self._session.refresh(task)
        return TaskResponse.model_validate(task)

    async def get_task(self, actor: ActorContext, task_id: str) -> TaskResponse:
        """Return one task visible to authorized workflow actors.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Task id to load.

        Returns:
            Matching task response.

        Raises:
            PermissionDenied: If the actor cannot view tasks.
            TaskNotFound: If the task id is unknown.
        """
        require_any_role(actor, TASK_VIEW_ROLES)
        task = await self._get_task(task_id)
        await self._ensure_task_visible(actor, task)
        return TaskResponse.model_validate(task)

    async def move_to_screening(
        self,
        actor: ActorContext,
        task_id: str,
        reason: str | None = None,
    ) -> TaskResponse:
        """Move a draft task to screening and lock active guide context.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Draft task to screen.
            reason: Optional transition reason stored in audit.

        Returns:
            Updated task response.

        Raises:
            PermissionDenied: If the actor cannot screen tasks.
            TaskNotFound: If the task id is unknown.
            TaskProjectNotReady: If active guide or policies are missing.
            TaskValidationError: If required task fields are incomplete.
        """
        require_any_role(actor, PROJECT_OPERATOR_ROLES)
        task = await self._get_task(task_id)
        self._ensure_transition_allowed(task.status, TASK_STATUS_SCREENING)

        guide, checker_policy, review_policy, revision_policy, payment_policy = (
            await self._load_active_policy_context(task.project_id)
        )
        self._validate_required_task_fields(task, guide)
        self._stamp_locked_context(
            task,
            guide,
            checker_policy,
            review_policy,
            revision_policy,
            payment_policy,
        )
        await self._change_task_status(actor, task, TASK_STATUS_SCREENING, reason)
        await self._session.commit()
        await self._session.refresh(task)
        return TaskResponse.model_validate(task)

    async def release_to_ready(
        self,
        actor: ActorContext,
        task_id: str,
        reason: str | None = None,
    ) -> TaskResponse:
        """Release a screened task to the ready queue.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Screened task to release.
            reason: Optional transition reason stored in audit.

        Returns:
            Updated task response.

        Raises:
            PermissionDenied: If the actor cannot release tasks.
            TaskTransitionBlocked: If locked policy context is incomplete.
        """
        require_any_role(actor, PROJECT_OPERATOR_ROLES)
        task = await self._get_task(task_id)
        self._ensure_transition_allowed(task.status, TASK_STATUS_READY)
        if reason is None or not reason.strip():
            raise TaskValidationError("release decision reason is required")
        self._ensure_locked_context(task)
        await self._change_task_status(actor, task, TASK_STATUS_READY, reason)
        await self._session.commit()
        await self._session.refresh(task)
        return TaskResponse.model_validate(task)

    async def claim_task(
        self,
        actor: ActorContext,
        task_id: str,
        reason: str | None = None,
    ) -> TaskWithAssignmentResponse:
        """Claim a ready task for the current actor.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Ready task to claim.
            reason: Optional transition reason stored in audit.

        Returns:
            Task and active assignment response.

        Raises:
            PermissionDenied: If the actor cannot claim tasks.
            TaskAssignmentConflict: If an active assignment already exists.
        """
        require_any_role(actor, TASK_CLAIM_ROLES)
        task = await self._get_task(task_id)
        self._ensure_transition_allowed(task.status, TASK_STATUS_CLAIMED)
        await self._require_active_worker_profile(actor)
        if await self._repo.get_active_assignment(task_id) is not None:
            raise TaskAssignmentConflict("task already has an active assignment")

        assignment = TaskAssignment(
            id=str(uuid4()),
            task_id=task.id,
            worker_id=actor.actor_id,
            assigned_by=actor.actor_id,
            accepted_at=datetime.now(UTC),
            status="active",
        )
        try:
            assignment = await self._repo.add_assignment(assignment)
            task.assigned_to = actor.actor_id
            await self._change_task_status(
                actor,
                task,
                TASK_STATUS_CLAIMED,
                reason,
                event_payload={"assignment_id": assignment.id, "worker_id": assignment.worker_id},
            )
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise TaskAssignmentConflict("task already has an active assignment") from exc
        await self._session.refresh(task)
        await self._session.refresh(assignment)
        return TaskWithAssignmentResponse(
            task=TaskResponse.model_validate(task),
            assignment=AssignmentResponse.model_validate(assignment),
        )

    async def start_task(
        self,
        actor: ActorContext,
        task_id: str,
        reason: str | None = None,
    ) -> TaskResponse:
        """Move a claimed task into active work.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Claimed task to start.
            reason: Optional transition reason stored in audit.

        Returns:
            Updated task response.

        Raises:
            PermissionDenied: If the actor cannot start this task.
            TaskTransitionBlocked: If no active assignment exists.
        """
        require_any_role(actor, TASK_START_ROLES)
        task = await self._get_task(task_id)
        self._ensure_transition_allowed(task.status, TASK_STATUS_IN_PROGRESS)
        assignment = await self._repo.get_active_assignment(task_id)
        if assignment is None:
            raise TaskTransitionBlocked("task has no active assignment")
        is_operator_override = assignment.worker_id != actor.actor_id and bool(
            set(actor.roles).intersection(TASK_START_OPERATOR_ROLES)
        )
        if assignment.worker_id != actor.actor_id and not is_operator_override:
            raise TaskTransitionBlocked("actor is not assigned to this task")
        if is_operator_override and (reason is None or not reason.strip()):
            raise TaskValidationError("operator start override reason is required")
        await self._change_task_status(
            actor,
            task,
            TASK_STATUS_IN_PROGRESS,
            reason,
            event_payload={
                "assignment_id": assignment.id,
                "worker_id": assignment.worker_id,
                "operator_override": bool(is_operator_override),
            },
            event_type="task_start_override" if is_operator_override else "task_status_changed",
        )
        await self._session.commit()
        await self._session.refresh(task)
        return TaskResponse.model_validate(task)

    async def list_task_audit_events(
        self,
        actor: ActorContext,
        task_id: str,
    ) -> list[AuditEventResponse]:
        """Return audit events for one task.

        Args:
            actor: Verified Flow actor context for the current request.
            task_id: Task whose audit trail should be loaded.

        Returns:
            Audit events ordered by creation time.
        """
        require_any_role(actor, TASK_VIEW_ROLES)
        task = await self._get_task(task_id)
        await self._ensure_task_visible(actor, task)
        events = await self._repo.list_audit_events("task", task.id)
        return [self._audit_response(event) for event in events]

    async def _get_task(self, task_id: str) -> WorkstreamTask:
        """Load a task or raise a service error.

        Args:
            task_id: Task id to load.

        Returns:
            Matching task model.

        Raises:
            TaskNotFound: If the task id is unknown.
        """
        task = await self._repo.get_task(task_id)
        if task is None:
            raise TaskNotFound("task not found")
        return task

    async def _load_active_policy_context(
        self,
        project_id: str,
    ) -> tuple[ProjectGuide, CheckerPolicy, ReviewPolicy, RevisionPolicy, PaymentPolicy]:
        """Load the active guide plus every policy needed for task locking.

        Args:
            project_id: Project whose active context should be loaded.

        Returns:
            Active guide and policy models.

        Raises:
            TaskProjectNotReady: If any required context is missing.
        """
        guide = await self._project_repo.get_active_guide(project_id)
        if guide is None:
            raise TaskProjectNotReady("project has no active guide")
        checker_policy = await self._project_repo.get_checker_policy(project_id, guide.version)
        review_policy = await self._project_repo.get_review_policy(project_id, guide.version)
        revision_policy = await self._project_repo.get_revision_policy(project_id, guide.version)
        payment_policy = await self._project_repo.get_payment_policy(project_id, guide.version)
        if (
            checker_policy is None
            or review_policy is None
            or revision_policy is None
            or payment_policy is None
        ):
            raise TaskProjectNotReady("active guide policy context is incomplete")
        return guide, checker_policy, review_policy, revision_policy, payment_policy

    def _validate_required_task_fields(self, task: WorkstreamTask, guide: ProjectGuide) -> None:
        """Validate guide-required task fields before screening.

        Args:
            task: Task being screened.
            guide: Active guide defining required task fields.

        Raises:
            TaskValidationError: If one or more required fields are missing.
        """
        required_fields = set(guide.required_task_fields or [])
        required_fields.update({"title", "description", "acceptance_criteria"})
        field_values = {
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "difficulty": task.difficulty,
            "skill_tags": task.skill_tags,
            "estimated_time_minutes": task.estimated_time_minutes,
            "acceptance_criteria": task.acceptance_criteria,
            "rejection_criteria": task.rejection_criteria,
            "required_files": task.required_files,
            "required_evidence": task.required_evidence,
            "deadline_at": task.deadline_at,
        }
        missing = [
            field
            for field in sorted(required_fields)
            if not self._field_has_value(field_values.get(field))
        ]
        if missing:
            raise TaskValidationError(f"task missing required fields: {', '.join(missing)}")

    @staticmethod
    def _field_has_value(value: object) -> bool:
        """Return whether a required field value is present.

        Args:
            value: Field value from the task model.

        Returns:
            ``True`` when the value should satisfy a required field.
        """
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list | tuple | set | dict):
            return bool(value)
        return True

    def _stamp_locked_context(
        self,
        task: WorkstreamTask,
        guide: ProjectGuide,
        checker_policy: CheckerPolicy,
        review_policy: ReviewPolicy,
        revision_policy: RevisionPolicy,
        payment_policy: PaymentPolicy,
    ) -> None:
        """Stamp server-owned guide and policy context onto a task.

        Args:
            task: Task receiving locked context.
            guide: Active guide.
            checker_policy: Checker policy for the guide version.
            review_policy: Review policy for the guide version.
            revision_policy: Revision policy for the guide version.
            payment_policy: Payment policy for the guide version.
        """
        task.locked_guide_version = guide.version
        task.locked_checker_policy_version = checker_policy.guide_version
        task.locked_review_policy_version = review_policy.guide_version
        task.locked_revision_policy_version = revision_policy.guide_version
        task.locked_payment_policy_version = payment_policy.guide_version
        task.base_amount = payment_policy.base_amount
        task.currency = payment_policy.currency
        task.payout_type = payment_policy.payout_type

    def _ensure_locked_context(self, task: WorkstreamTask) -> None:
        """Ensure all guide and policy version fields are locked.

        Args:
            task: Task whose locked context should be checked.

        Raises:
            TaskTransitionBlocked: If any context field is missing.
        """
        missing = [
            field
            for field in (
                "locked_guide_version",
                "locked_checker_policy_version",
                "locked_review_policy_version",
                "locked_revision_policy_version",
                "locked_payment_policy_version",
            )
            if not getattr(task, field)
        ]
        if missing:
            raise TaskTransitionBlocked(f"task missing locked context: {', '.join(missing)}")

    async def _require_active_worker_profile(
        self,
        actor: ActorContext,
    ) -> WorkerProfile:
        """Require an active worker profile before claim.

        Args:
            actor: Verified Flow actor context.

        Returns:
            Persisted active worker profile.

        Raises:
            WorkerProfileRequired: If the actor has no active worker profile.
        """
        profile = await self._repo.get_worker_profile(actor.actor_id)
        if profile is None or profile.status != "active":
            raise WorkerProfileRequired("active worker profile is required to claim task")
        return profile

    async def ensure_reviewer_profile(
        self,
        actor: ActorContext,
        skill_tags: list[str],
    ) -> ReviewerProfile:
        """Create or refresh a reviewer profile for the current actor.

        Args:
            actor: Verified Flow actor context.
            skill_tags: Skill tags to associate with the reviewer.

        Returns:
            Persisted reviewer profile.
        """
        require_any_role(actor, {"admin", "project_manager", "reviewer"})
        return await self._repo.upsert_reviewer_profile(
            ReviewerProfile(
                id=str(uuid4()),
                actor_id=actor.actor_id,
                external_subject=actor.external_subject,
                external_issuer=actor.external_issuer,
                display_name=actor.display_name,
                email=actor.email,
                skill_tags=skill_tags,
                status="active",
            )
        )

    async def _change_task_status(
        self,
        actor: ActorContext,
        task: WorkstreamTask,
        to_status: str,
        reason: str | None,
        event_payload: dict | None = None,
        event_type: str = "task_status_changed",
    ) -> None:
        """Apply a lifecycle transition and write the audit event.

        Args:
            actor: Verified Flow actor context.
            task: Task being transitioned.
            to_status: Next task status.
            reason: Optional transition reason for audit.
            event_payload: Structured event details to store with the audit event.
            event_type: Audit event type.
        """
        from_status = task.status
        self._ensure_transition_allowed(from_status, to_status)
        task.status = to_status
        await self._write_task_audit(
            actor,
            task,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            event_payload=event_payload,
        )

    async def _write_task_audit(
        self,
        actor: ActorContext,
        task: WorkstreamTask,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        reason: str | None,
        event_payload: dict | None = None,
    ) -> None:
        """Persist an actor-attributed task audit event.

        Args:
            actor: Verified Flow actor context.
            task: Task associated with the event.
            event_type: Type of audit event.
            from_status: Previous task status when applicable.
            to_status: New task status when applicable.
            reason: Optional event reason.
            event_payload: Optional structured event metadata.
        """
        audit = actor.audit_context()
        payload = {
            "locked_guide_version": task.locked_guide_version,
            "locked_checker_policy_version": task.locked_checker_policy_version,
            "locked_review_policy_version": task.locked_review_policy_version,
            "locked_revision_policy_version": task.locked_revision_policy_version,
            "locked_payment_policy_version": task.locked_payment_policy_version,
            "assigned_to": task.assigned_to,
        }
        if event_payload:
            payload.update(event_payload)
        await self._repo.add_audit_event(
            AuditEvent(
                id=str(uuid4()),
                entity_type="task",
                entity_id=task.id,
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                actor_id=audit.actor_id,
                external_subject=audit.external_subject,
                external_issuer=audit.external_issuer,
                actor_roles=list(audit.actor_roles),
                claim_snapshot=audit.claim_snapshot,
                auth_source=audit.auth_source,
                is_dev_auth=audit.is_dev_auth,
                reason=reason,
                event_payload=payload,
            )
        )

    async def _ensure_task_visible(self, actor: ActorContext, task: WorkstreamTask) -> None:
        """Apply object-level task visibility rules.

        Args:
            actor: Verified Flow actor context.
            task: Task being read.

        Raises:
            TaskNotFound: If the actor has no object-level visibility.
        """
        roles = set(actor.roles)
        if roles.intersection({"admin", "project_manager", "auditor"}):
            return
        if "worker" in roles:
            if task.status == TASK_STATUS_READY or task.assigned_to == actor.actor_id:
                return
        raise TaskNotFound("task not found")

    def _audit_response(self, event: AuditEvent) -> AuditEventResponse:
        """Build a public audit response with claim snapshots redacted.

        Args:
            event: Persisted audit event.

        Returns:
            Audit response safe for the current task audit endpoint.
        """
        response = AuditEventResponse.model_validate(event)
        response.claim_snapshot = {}
        return response

    def _ensure_transition_allowed(self, from_status: str, to_status: str) -> None:
        """Map lifecycle transition validation into service-layer errors.

        Args:
            from_status: Current task status.
            to_status: Desired next task status.

        Raises:
            TaskTransitionBlocked: If the transition is not implemented by this chunk.
        """
        try:
            ensure_allowed_transition(from_status, to_status)
        except InvalidTaskTransition as exc:
            raise TaskTransitionBlocked(str(exc)) from exc
