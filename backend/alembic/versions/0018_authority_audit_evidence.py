"""add append-only authority audit evidence

Revision ID: 0018_authority_audit_evidence
Revises: 0017_api_controls
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_authority_audit_evidence"
down_revision = "0017_api_controls"
branch_labels = None
depends_on = None

AUTHORITY_EVENT_TYPES = (
    "ActorProfileProvisioned",
    "ServiceActorProvisioned",
    "ActorIdentityLinked",
    "ActorIdentityLinkRevoked",
    "ActorIdentityLinkReactivated",
    "ActorProfileSuspended",
    "ActorProfileReactivated",
    "ActorProfileDeactivated",
    "InitialAccessAdministratorBootstrapped",
    "AdminRoleGrantIssued",
    "AdminRoleGrantRevoked",
    "AdminRoleGrantIssueDenied",
    "LastAccessAdministratorOperationDenied",
    "ProjectRoleQualificationSnapshotCaptured",
    "ProjectRoleGrantIssued",
    "ProjectRoleGrantReplaced",
    "ProjectRoleGrantRevoked",
    "SensitiveAuthorizationAllowed",
    "SensitiveAuthorizationDenied",
    "AuthorityInvalidationRequested",
)


def upgrade() -> None:
    """Extend the shared audit table and install normal-DML custody guards."""
    columns = (
        sa.Column(
            "event_domain",
            sa.String(24),
            nullable=False,
            server_default="legacy_lifecycle",
        ),
        sa.Column("event_version", sa.Integer(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actor_ref_kind", sa.String(32), nullable=True),
        sa.Column("request_id", sa.Uuid(), nullable=True),
        sa.Column("correlation_id", sa.Uuid(), nullable=True),
        sa.Column("target_actor_ref_kind", sa.String(32), nullable=True),
        sa.Column("target_actor_ref", sa.String(100), nullable=True),
        sa.Column("matched_grant_id", sa.String(100), nullable=True),
        sa.Column("permission_id", sa.String(120), nullable=True),
        sa.Column("project_id", sa.String(36), nullable=True),
        sa.Column("resource_type", sa.String(80), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("target_ref_kind", sa.String(32), nullable=True),
        sa.Column("target_ref_id", sa.String(100), nullable=True),
        sa.Column("denial_code", sa.String(80), nullable=True),
        sa.Column("idempotency_reference", sa.Uuid(), nullable=True),
        sa.Column("invalidation_cause_event_id", sa.String(36), nullable=True),
        sa.Column("invalidation_target_kind", sa.String(32), nullable=True),
        sa.Column("invalidation_target_ref", sa.String(100), nullable=True),
        sa.Column("before_facts", sa.JSON(), nullable=True),
        sa.Column("after_facts", sa.JSON(), nullable=True),
    )
    for column in columns:
        op.add_column("audit_events", column)
    op.alter_column("audit_events", "external_subject", existing_type=sa.String(200), nullable=True)
    op.alter_column("audit_events", "external_issuer", existing_type=sa.String(200), nullable=True)
    op.execute("""create function authority_facts_are_safe(facts json) returns boolean language sql immutable strict as $$
      select json_typeof(facts) = 'object' and not exists (select 1 from json_each(facts) item where
        item.key not in ('status','subject_kind','provisioning_method','link_status','role_id','scope_type','scope_id','effective','qualification_status','decision_code','target_status')
        or json_typeof(item.value) not in ('string','boolean','null')
        or (item.key = 'effective' and json_typeof(item.value) not in ('boolean','null'))
        or (item.key <> 'effective' and json_typeof(item.value) not in ('string','null'))
        or (json_typeof(item.value) = 'string' and ((item.value #>> '{}') ~ '^eyJ' or (item.key in ('role_id','scope_id') and (item.value #>> '{}') !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$') or (item.key not in ('role_id','scope_id') and (item.value #>> '{}') !~ '^[a-z][a-z0-9_]{0,79}$')))) $$""")

    event_tokens = ", ".join(f"'{value}'" for value in AUTHORITY_EVENT_TYPES)
    op.create_check_constraint(
        "domain_shape",
        "audit_events",
        """
        (event_domain = 'legacy_lifecycle' and event_version is null and occurred_at is null and actor_ref_kind is null and request_id is null and correlation_id is null
          and target_actor_ref_kind is null and target_actor_ref is null and matched_grant_id is null and permission_id is null and project_id is null
          and resource_type is null and resource_id is null and target_ref_kind is null and target_ref_id is null and denial_code is null
          and idempotency_reference is null and invalidation_cause_event_id is null and invalidation_target_kind is null and invalidation_target_ref is null
          and before_facts is null and after_facts is null and external_subject is not null and external_issuer is not null)
        or (event_domain = 'authority' and event_version = 1 and occurred_at is not null and actor_ref_kind in ('legacy_actor','actor_profile','system_principal')
          and request_id is not null and correlation_id is not null and from_status is null and to_status is null and (reason is null or length(reason) <= 1000)
          and external_subject is null and external_issuer is null and actor_roles::jsonb = '[]'::jsonb and claim_snapshot::jsonb = '{}'::jsonb and auth_source = 'local_authority' and is_dev_auth = false and event_payload::jsonb = '{}'::jsonb)
        """,
    )
    op.create_check_constraint(
        "authority_tokens",
        "audit_events",
        f"event_domain <> 'authority' or event_type in ({event_tokens})",
    )
    op.create_check_constraint(
        "reference_pairs",
        "audit_events",
        """
        (target_actor_ref_kind is null) = (target_actor_ref is null) and (resource_type is null) = (resource_id is null)
        and (target_ref_kind is null) = (target_ref_id is null) and (invalidation_target_kind is null) = (invalidation_target_ref is null)
        and (invalidation_cause_event_id is null or invalidation_cause_event_id <> id)
        """,
    )
    op.create_check_constraint(
        "authority_privacy_bounds",
        "audit_events",
        """
        event_domain <> 'authority' or ((((actor_ref_kind in ('legacy_actor','actor_profile') and actor_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
          or (actor_ref_kind = 'system_principal' and actor_id ~ '^[a-z][a-z0-9_]*(:[a-z][a-z0-9_-]*)+$'))
          and (target_actor_ref is null or ((target_actor_ref_kind in ('legacy_actor','actor_profile') and target_actor_ref ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
          or (target_actor_ref_kind = 'system_principal' and target_actor_ref ~ '^[a-z][a-z0-9_]*(:[a-z][a-z0-9_-]*)+$')))
          and entity_id ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,35}$' and concat_ws('',matched_grant_id,permission_id,project_id,resource_type,resource_id,target_ref_kind,target_ref_id,denial_code,invalidation_target_kind,invalidation_target_ref) !~ '[/@[:space:]]'
          and (reason is null or reason ~ '^[A-Za-z0-9][A-Za-z0-9 _.,:;()!?-]*$')))
        """,
    )
    op.create_check_constraint(
        "fact_bounds",
        "audit_events",
        "(before_facts is null or (authority_facts_are_safe(before_facts) and octet_length(before_facts::text) <= 4096)) and (after_facts is null or (authority_facts_are_safe(after_facts) and octet_length(after_facts::text) <= 4096))",
    )
    op.create_foreign_key(
        "fk_audit_events_invalidation_cause",
        "audit_events",
        "audit_events",
        ["invalidation_cause_event_id"],
        ["id"],
    )
    op.create_check_constraint(
        "foundation_shapes",
        "audit_events",
        """
        event_domain <> 'authority' or event_type not in ('SensitiveAuthorizationAllowed','SensitiveAuthorizationDenied','AuthorityInvalidationRequested')
        or (event_type = 'SensitiveAuthorizationAllowed' and permission_id is not null and denial_code is null and invalidation_cause_event_id is null and invalidation_target_kind is null)
        or (event_type = 'SensitiveAuthorizationDenied' and permission_id is not null and denial_code is not null and invalidation_cause_event_id is null and invalidation_target_kind is null and idempotency_reference is null)
        or (event_type = 'AuthorityInvalidationRequested' and invalidation_cause_event_id is not null and invalidation_target_kind is not null and denial_code is null)
        """,
    )
    for name, fields in (
        ("ix_audit_events_request_id", ["request_id"]),
        ("ix_audit_events_correlation_id", ["correlation_id"]),
        ("ix_audit_events_occurred_at", ["occurred_at"]),
        ("ix_audit_events_project_id", ["project_id"]),
        ("ix_audit_events_actor_ref", ["actor_ref_kind", "actor_id"]),
    ):
        op.create_index(name, "audit_events", fields)

    op.execute("""create function set_authority_audit_database_time() returns trigger language plpgsql as $$ begin
      if new.event_domain = 'authority' then
        if new.invalidation_cause_event_id is not null and not exists (select 1 from audit_events where id = new.invalidation_cause_event_id and event_domain = 'authority') then
          raise exception 'invalid authority invalidation cause' using errcode = '23503'; end if;
        new.occurred_at = statement_timestamp();
      else new.occurred_at = null; end if; return new; end $$""")
    op.execute("create trigger audit_events_set_authority_time before insert on audit_events for each row execute function set_authority_audit_database_time()")
    op.execute("""create function reject_audit_event_mutation() returns trigger language plpgsql as $$ begin raise exception 'audit events are append-only' using errcode = '55000'; end $$""")
    op.execute("create trigger audit_events_reject_update_delete before update or delete on audit_events for each row execute function reject_audit_event_mutation()")
    op.execute("create trigger audit_events_reject_truncate before truncate on audit_events for each statement execute function reject_audit_event_mutation()")


def downgrade() -> None:
    """Remove only unused authority-envelope schema while preserving legacy rows."""
    bind = op.get_bind()
    bind.execute(sa.text("lock table audit_events in access exclusive mode"))
    has_authority = bind.execute(
        sa.text("select exists(select 1 from audit_events where event_domain = 'authority')")
    ).scalar_one()
    if has_authority:
        raise RuntimeError("cannot downgrade non-empty authority audit evidence")

    for trigger in (
        "audit_events_reject_truncate",
        "audit_events_reject_update_delete",
        "audit_events_set_authority_time",
    ):
        op.execute(f"drop trigger {trigger} on audit_events")
    op.execute("drop function reject_audit_event_mutation()")
    op.execute("drop function set_authority_audit_database_time()")
    for name in (
        "ix_audit_events_actor_ref",
        "ix_audit_events_project_id",
        "ix_audit_events_occurred_at",
        "ix_audit_events_correlation_id",
        "ix_audit_events_request_id",
    ):
        op.drop_index(name, table_name="audit_events")
    op.drop_constraint("fk_audit_events_invalidation_cause", "audit_events", type_="foreignkey")
    for name in (
        "foundation_shapes",
        "fact_bounds",
        "authority_privacy_bounds",
        "reference_pairs",
        "authority_tokens",
        "domain_shape",
    ):
        op.drop_constraint(name, "audit_events", type_="check")
    op.execute("drop function authority_facts_are_safe(json)")
    for column in reversed(
        (
            "event_version", "occurred_at", "actor_ref_kind", "request_id", "correlation_id",
            "target_actor_ref_kind", "target_actor_ref", "matched_grant_id", "permission_id",
            "project_id", "resource_type", "resource_id", "target_ref_kind", "target_ref_id",
            "denial_code", "idempotency_reference", "invalidation_cause_event_id",
            "invalidation_target_kind", "invalidation_target_ref", "before_facts", "after_facts",
            "event_domain",
        )
    ):
        op.drop_column("audit_events", column)
    op.alter_column("audit_events", "external_issuer", existing_type=sa.String(200), nullable=False)
    op.alter_column("audit_events", "external_subject", existing_type=sa.String(200), nullable=False)
