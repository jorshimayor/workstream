"""Import domain models so Alembic can discover metadata."""

from app.modules.checkers.models import CheckerResult, CheckerRun  # noqa: F401
from app.modules.projects.models import (  # noqa: F401
    CheckerPolicy,
    PaymentPolicy,
    Project,
    ProjectGuide,
    RevisionPolicy,
    ReviewPolicy,
)
from app.modules.tasks.models import (  # noqa: F401
    AuditEvent,
    EvidenceItem,
    ReviewerProfile,
    Submission,
    TaskAssignment,
    WorkerProfile,
    WorkstreamTask,
)
