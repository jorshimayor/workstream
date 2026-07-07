from __future__ import annotations

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.auth.dev import actor_id_from_external_identity

def test_alembic_upgrade_and_downgrade(isolated_database_env: str, migration_lock) -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    with migration_lock():
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        command.downgrade(config, "base")


def test_current_schema_uses_project_policy_contract(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove current schema stores guide prose and policy records separately."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "head")
            columns = asyncio.run(_fetch_columns(isolated_database_env))
        finally:
            command.downgrade(config, "base")

    assert {
        "projects.id",
        "projects.name",
        "projects.slug",
        "projects.status",
        "project_guides.content_markdown",
        "project_guides.approved_by",
        "project_guides.effective_at",
        "submission_artifact_policies.policy_body",
        "effective_project_submission_artifact_policies.effective_policy",
        "pre_submit_checker_policies.compiled_bundle",
        "payment_policies.base_amount",
        "payment_policies.currency",
    }.issubset(columns)
    discarded_columns = {
        "projects.base_amount",
        "projects.currency",
        "project_guides.required_task_fields",
        "project_guides.required_submission_fields",
        "project_guides.task_instructions",
        "project_guides.output_requirements",
        "project_guides.acceptance_criteria",
        "project_guides.rejection_criteria",
        "project_guides.reviewer_rubric",
        "project_guides.forbidden_actions",
        "project_guides.required_skills",
        "project_guides.difficulty_scale",
        "project_guides.estimated_time_policy",
        "project_guides.common_rejection_reasons",
        "project_guides.evidence_policy",
        "project_guides.unacceptable_work_policy",
        "workstream_tasks.required_files",
        "workstream_tasks.required_evidence",
        "workstream_tasks.locked_checker_policy_version",
        "submissions.locked_checker_policy_version",
        "checker_runs.locked_checker_policy_version",
    }
    assert columns.isdisjoint(discarded_columns)


def test_post_submit_policy_upgrade_leaves_pre_provenance_rows_fail_closed(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove 0008 does not create fake post-submit authority for pre-provenance rows."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    pre_provenance_project_id = str(uuid4())
    pre_provenance_guide_id = str(uuid4())
    pre_provenance_policy_id = str(uuid4())
    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "0007_task_locked_context")
            asyncio.run(
                _seed_pre_provenance_post_submit_policy(
                    isolated_database_env,
                    pre_provenance_project_id,
                    pre_provenance_guide_id,
                    pre_provenance_policy_id,
                )
            )
            command.upgrade(config, "0008_post_submit_checker_policy")
            policy_hash = asyncio.run(
                _fetch_pre_provenance_post_submit_policy_hash(
                    isolated_database_env,
                    pre_provenance_policy_id,
                )
            )
        finally:
            command.downgrade(config, "base")

    assert policy_hash is None


def test_post_submit_policy_upgrade_blocks_pre_provenance_runtime_rows(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove 0008 fails clearly when runtime rows cannot gain trusted provenance."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    ids = {name: str(uuid4()) for name in ("project", "guide", "policy", "task", "submission", "run")}
    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "0007_task_locked_context")
            asyncio.run(_seed_pre_provenance_runtime_rows(isolated_database_env, ids))

            with pytest.raises(RuntimeError, match="cannot infer locked post-submit"):
                command.upgrade(config, "0008_post_submit_checker_policy")

            columns_exist = asyncio.run(
                _post_submit_lock_columns_exist(isolated_database_env, "submissions")
            )
        finally:
            command.downgrade(config, "base")

    assert columns_exist is False


def test_actor_profile_registry_removes_obsolete_profile_tables(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove obsolete profile tables are removed from the current schema."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "head")
            table_names = asyncio.run(_fetch_table_names(isolated_database_env))
        finally:
            command.downgrade(config, "base")

    assert "actor_identities" in table_names
    assert "actor_profiles" in table_names
    assert "worker_profiles" not in table_names
    assert "reviewer_profiles" not in table_names


def test_actor_profile_registry_unique_constraints_are_enforced(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove actor registry uniqueness is enforced by Postgres."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "head")
            asyncio.run(_assert_actor_registry_unique_constraints(isolated_database_env))
        finally:
            command.downgrade(config, "base")


async def _fetch_columns(database_url: str) -> set[str]:
    """Return current public table columns as table.column names."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            rows = (
                await connection.execute(
                    text(
                        """
                        select table_name, column_name
                        from information_schema.columns
                        where table_schema = 'public'
                        """
                    )
                )
            ).all()
            return {f"{row.table_name}.{row.column_name}" for row in rows}
    finally:
        await engine.dispose()


async def _fetch_table_names(database_url: str) -> set[str]:
    """Return current public table names."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            rows = (
                await connection.execute(
                    text(
                        """
                        select table_name
                        from information_schema.tables
                        where table_schema = 'public'
                        """
                    )
                )
            ).all()
            return {row.table_name for row in rows}
    finally:
        await engine.dispose()


async def _assert_actor_registry_unique_constraints(database_url: str) -> None:
    """Insert duplicates and prove actor registry unique constraints reject them."""
    engine = create_async_engine(database_url)
    actor_id = actor_id_from_external_identity("flow-test", "unique-actor")
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into actor_identities (
                        actor_id,
                        external_subject,
                        external_issuer,
                        display_name,
                        email,
                        last_seen_roles,
                        last_claim_snapshot,
                        auth_source,
                        is_dev_auth
                    )
                    values (
                        :actor_id,
                        'unique-actor',
                        'flow-test',
                        'Unique Actor',
                        'unique@example.test',
                        cast(:roles as json),
                        cast(:claim_snapshot as json),
                        'dev_mock',
                        true
                    )
                    """
                ),
                {
                    "actor_id": actor_id,
                    "roles": json.dumps(["worker"]),
                    "claim_snapshot": json.dumps({"roles": ["worker"]}),
                },
            )
            await connection.execute(
                text(
                    """
                    insert into actor_profiles (
                        id,
                        actor_id,
                        profile_type,
                        status,
                        skill_tags,
                        scope_type,
                        scope_id,
                        profile_metadata
                    )
                    values (
                        :id,
                        :actor_id,
                        'worker',
                        'observed',
                        cast(:skill_tags as json),
                        'global',
                        'global',
                        cast(:profile_metadata as json)
                    )
                    """
                ),
                {
                    "id": str(uuid4()),
                    "actor_id": actor_id,
                    "skill_tags": json.dumps([]),
                    "profile_metadata": json.dumps({}),
                },
            )

        duplicate_actor_id = text(
            """
            insert into actor_identities (
                actor_id,
                external_subject,
                external_issuer,
                last_seen_roles,
                last_claim_snapshot,
                auth_source,
                is_dev_auth
            )
            values (
                :actor_id,
                'different-subject',
                'flow-test',
                cast(:roles as json),
                cast(:claim_snapshot as json),
                'dev_mock',
                true
            )
            """
        )
        duplicate_external_identity = text(
            """
            insert into actor_identities (
                actor_id,
                external_subject,
                external_issuer,
                last_seen_roles,
                last_claim_snapshot,
                auth_source,
                is_dev_auth
            )
            values (
                :actor_id,
                'unique-actor',
                'flow-test',
                cast(:roles as json),
                cast(:claim_snapshot as json),
                'dev_mock',
                true
            )
            """
        )
        duplicate_profile_scope = text(
            """
            insert into actor_profiles (
                id,
                actor_id,
                profile_type,
                status,
                skill_tags,
                scope_type,
                scope_id,
                profile_metadata
            )
            values (
                :id,
                :actor_id,
                'worker',
                'observed',
                cast(:skill_tags as json),
                'global',
                'global',
                cast(:profile_metadata as json)
            )
            """
        )
        await _expect_integrity_error(
            engine,
            duplicate_actor_id,
            {
                "actor_id": actor_id,
                "roles": json.dumps([]),
                "claim_snapshot": json.dumps({}),
            },
        )
        await _expect_integrity_error(
            engine,
            duplicate_external_identity,
            {
                "actor_id": actor_id_from_external_identity("flow-test", "other-unique-actor"),
                "roles": json.dumps([]),
                "claim_snapshot": json.dumps({}),
            },
        )
        await _expect_integrity_error(
            engine,
            duplicate_profile_scope,
            {
                "id": str(uuid4()),
                "actor_id": actor_id,
                "skill_tags": json.dumps([]),
                "profile_metadata": json.dumps({}),
            },
        )
    finally:
        await engine.dispose()


async def _expect_integrity_error(engine, statement, params: dict) -> None:
    """Assert that one SQL statement raises a database integrity error."""
    with pytest.raises(IntegrityError):
        async with engine.begin() as connection:
            await connection.execute(statement, params)


async def _seed_pre_provenance_post_submit_policy(
    database_url: str,
    project_id: str,
    guide_id: str,
    policy_id: str,
) -> None:
    """Seed a valid 0007 checker policy row before post-submit hashes exist."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into projects (
                        id,
                        name,
                        slug,
                        status
                    )
                    values (
                        :project_id,
                        'Pre-provenance policy project',
                        'pre-provenance-policy-project',
                        'draft'
                    )
                    """
                ),
                {"project_id": project_id},
            )
            await connection.execute(
                text(
                    """
                    insert into project_guides (
                        id,
                        project_id,
                        version,
                        status,
                        content_markdown,
                        created_by
                    )
                    values (
                        :guide_id,
                        :project_id,
                        'v1',
                        'draft',
                        '# Pre-provenance guide',
                        'pre-provenance-test'
                    )
                    """
                ),
                {"guide_id": guide_id, "project_id": project_id},
            )
            await connection.execute(
                text(
                    """
                    insert into checker_policies (
                        id,
                        project_id,
                        guide_version,
                        required_checkers,
                        warning_checkers,
                        blocking_severities
                    )
                    values (
                        :policy_id,
                        :project_id,
                        'v1',
                        '["check_policy_context_present"]'::json,
                        '[]'::json,
                        '["high"]'::json
                    )
                    """
                ),
                {"policy_id": policy_id, "project_id": project_id},
            )
    finally:
        await engine.dispose()


async def _seed_pre_provenance_runtime_rows(database_url: str, ids: dict[str, str]) -> None:
    """Seed 0007 runtime rows that cannot be trusted under 0008 provenance."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into projects (
                        id,
                        name,
                        slug,
                        status
                    )
                    values (
                        :project_id,
                        'Pre-provenance runtime project',
                        'pre-provenance-runtime-project',
                        'draft'
                    )
                    """
                ),
                {"project_id": ids["project"]},
            )
            await connection.execute(
                text(
                    """
                    insert into project_guides (
                        id,
                        project_id,
                        version,
                        status,
                        content_markdown,
                        created_by
                    )
                    values (
                        :guide_id,
                        :project_id,
                        'v1',
                        'active',
                        '# Pre-provenance runtime guide',
                        'pre-provenance-test'
                    )
                    """
                ),
                {"guide_id": ids["guide"], "project_id": ids["project"]},
            )
            await _seed_pre_provenance_policies(connection, ids["project"], ids["policy"])
            await connection.execute(
                text(
                    """
                    insert into workstream_tasks (
                        id,
                        project_id,
                        locked_guide_version,
                        locked_review_policy_version,
                        locked_revision_policy_version,
                        locked_payment_policy_version,
                        source_type,
                        title,
                        description,
                        skill_tags,
                        status,
                        created_by
                    )
                    values (
                        :task_id,
                        :project_id,
                        'v1',
                        'v1',
                        'v1',
                        'v1',
                        'manual',
                        'Pre-provenance runtime task',
                        'Already in progress before 0008.',
                        '[]'::json,
                        'in_progress',
                        'pre-provenance-test'
                    )
                    """
                ),
                {"task_id": ids["task"], "project_id": ids["project"]},
            )
            await connection.execute(
                text(
                    """
                    insert into submissions (
                        id,
                        task_id,
                        worker_id,
                        version,
                        status,
                        summary,
                        package_hash,
                        artifact_hash_manifest,
                        worker_attestation,
                        locked_guide_version,
                        locked_review_policy_version,
                        locked_revision_policy_version,
                        locked_payment_policy_version
                    )
                    values (
                        :submission_id,
                        :task_id,
                        'pre-provenance-worker',
                        1,
                        'submitted',
                        'Pre-provenance submitted packet',
                        'sha256:pre-provenance-package',
                        '[]'::json,
                        'pre-provenance attestation',
                        'v1',
                        'v1',
                        'v1',
                        'v1'
                    )
                    """
                ),
                {"submission_id": ids["submission"], "task_id": ids["task"]},
            )
            await connection.execute(
                text(
                    """
                    insert into checker_runs (
                        id,
                        task_id,
                        submission_id,
                        submission_version,
                        trigger_source,
                        status,
                        routing_recommendation,
                        outcome_source,
                        triggered_by,
                        triggered_by_subject,
                        triggered_by_issuer,
                        trigger_auth_source,
                        attempt_number,
                        is_current_for_submission,
                        locked_guide_version,
                        locked_review_policy_version,
                        locked_revision_policy_version,
                        locked_payment_policy_version,
                        package_hash,
                        artifact_hash_manifest,
                        artifact_manifest_hash,
                        passed_count,
                        warning_count,
                        failed_count,
                        blocking_count
                    )
                    values (
                        :run_id,
                        :task_id,
                        :submission_id,
                        1,
                        'submission_lock',
                        'completed',
                        'allow_review',
                        'auto_checker',
                        'pre-provenance-test',
                        'pre-provenance-test',
                        'flow-pre-provenance',
                        'flow',
                        1,
                        true,
                        'v1',
                        'v1',
                        'v1',
                        'v1',
                        'sha256:pre-provenance-package',
                        '[]'::json,
                        'sha256:pre-provenance-manifest',
                        1,
                        0,
                        0,
                        0
                    )
                    """
                ),
                {
                    "run_id": ids["run"],
                    "task_id": ids["task"],
                    "submission_id": ids["submission"],
                },
            )
    finally:
        await engine.dispose()


async def _seed_pre_provenance_policies(connection, project_id: str, checker_policy_id: str) -> None:
    """Seed v0.1 guide policies required by locked task foreign keys."""
    await connection.execute(
        text(
            """
            insert into checker_policies (
                id,
                project_id,
                guide_version,
                required_checkers,
                warning_checkers,
                blocking_severities
            )
            values (
                :checker_policy_id,
                :project_id,
                'v1',
                '["check_policy_context_present"]'::json,
                '[]'::json,
                '["high"]'::json
            )
            """
        ),
        {"checker_policy_id": checker_policy_id, "project_id": project_id},
    )
    await connection.execute(
        text(
            """
            insert into review_policies (
                id,
                project_id,
                guide_version,
                requires_second_review,
                allowed_decisions,
                minimum_finding_fields
            )
            values (
                :review_policy_id,
                :project_id,
                'v1',
                false,
                '["accept", "needs_revision", "reject"]'::json,
                '[]'::json
            )
            """
        ),
        {"review_policy_id": str(uuid4()), "project_id": project_id},
    )
    await connection.execute(
        text(
            """
            insert into revision_policies (
                id,
                project_id,
                guide_version,
                max_revision_rounds,
                revision_deadline_hours,
                auto_reject_after_limit,
                allowed_resubmission_states
            )
            values (
                :revision_policy_id,
                :project_id,
                'v1',
                7,
                48,
                true,
                '["needs_revision"]'::json
            )
            """
        ),
        {"revision_policy_id": str(uuid4()), "project_id": project_id},
    )
    await connection.execute(
        text(
            """
            insert into payment_policies (
                id,
                project_id,
                guide_version,
                base_amount,
                currency,
                payout_type
            )
            values (
                :payment_policy_id,
                :project_id,
                'v1',
                25.00,
                'USD',
                'fixed'
            )
            """
        ),
        {"payment_policy_id": str(uuid4()), "project_id": project_id},
    )


async def _post_submit_lock_columns_exist(database_url: str, table_name: str) -> bool:
    """Return whether a post-submit lock column was added to a table."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            count = await connection.scalar(
                text(
                    """
                    select count(*)
                    from information_schema.columns
                    where table_name = :table_name
                      and column_name = 'locked_post_submit_checker_policy_id'
                    """
                ),
                {"table_name": table_name},
            )
            return bool(count)
    finally:
        await engine.dispose()


async def _fetch_pre_provenance_post_submit_policy_hash(
    database_url: str,
    policy_id: str,
) -> str | None:
    """Return the post-submit policy hash created by the 0008 migration, if any."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            return await connection.scalar(
                text("select policy_hash from checker_policies where id = :policy_id"),
                {"policy_id": policy_id},
            )
    finally:
        await engine.dispose()
