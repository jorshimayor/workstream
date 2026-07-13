from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading
import time
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
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
        "checker_policies.source_snapshot_id",
        "checker_policies.source_snapshot_hash",
        "checker_policies.effective_policy_id",
        "checker_policies.effective_policy_hash",
        "checker_policies.pre_submit_checker_policy_id",
        "checker_policies.pre_submit_checker_bundle_hash",
        "payment_policies.base_amount",
        "payment_policies.currency",
        "artifact_upload_sessions.id",
        "artifact_upload_items.id",
        "artifact_contents.sha256",
        "artifact_bindings.scope_version",
        "artifact_replicas.provider_artifact_id",
        "artifact_operation_receipts.request_digest",
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


def test_artifact_foundation_upgrade_preserves_prior_head_and_promotes_nothing(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Upgrade populated 0015 data without interpreting legacy declarations."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    project_id = str(uuid4())
    runtime_ids = {
        name: str(uuid4())
        for name in (
            "project",
            "guide",
            "snapshot",
            "submission_policy",
            "effective_policy",
            "pre_submit_policy",
            "policy",
            "review_policy",
            "revision_policy",
            "payment_policy",
            "task",
            "submission",
            "run",
        )
    }
    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "0015_post_submit_correction")
            asyncio.run(_seed_artifact_prior_head(isolated_database_env, project_id))
            asyncio.run(_seed_artifact_prior_head_runtime_rows(isolated_database_env, runtime_ids))
            before = asyncio.run(_artifact_prior_head_project(isolated_database_env, project_id))
            runtime_before = asyncio.run(
                _artifact_prior_head_runtime_rows(isolated_database_env, runtime_ids)
            )
            command.upgrade(config, "0016_artifact_domain")
            after = asyncio.run(_artifact_prior_head_project(isolated_database_env, project_id))
            runtime_after = asyncio.run(
                _artifact_prior_head_runtime_rows(isolated_database_env, runtime_ids)
            )
            artifact_counts = asyncio.run(_artifact_table_counts(isolated_database_env))
        finally:
            command.downgrade(config, "base")

    assert after == before
    assert runtime_after == runtime_before
    assert artifact_counts == {name: 0 for name in artifact_counts}


def test_artifact_foundation_enforces_immutable_facts_and_guarded_downgrade(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove PostgreSQL rejects malformed/mutable facts and non-empty downgrade."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    ids = {
        name: str(uuid4())
        for name in (
            "project",
            "content",
            "session",
            "item",
            "replica",
            "receipt",
            "binding",
            "binding_v2",
        )
    }
    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "0016_artifact_domain")
            asyncio.run(_assert_artifact_fact_guards(isolated_database_env, ids))
            with pytest.raises(RuntimeError, match="non-empty artifact foundation"):
                command.downgrade(config, "0015_post_submit_correction")
            asyncio.run(_truncate_artifact_foundation(isolated_database_env))
            command.downgrade(config, "0015_post_submit_correction")
            command.upgrade(config, "0016_artifact_domain")
            assert all(
                count == 0
                for count in asyncio.run(
                    _artifact_table_counts(isolated_database_env)
                ).values()
            )
        finally:
            command.downgrade(config, "base")


def test_api_rate_control_schema_preserves_domain_and_guards_downgrade(
    isolated_database_env: str,
    migration_lock,
) -> None:
    """Prove 0017 schema guards, preservation, and transactional downgrade refusal."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    project_id = str(uuid4())
    artifact_id = str(uuid4())
    digest = bytes(range(32))

    with migration_lock():
        try:
            command.downgrade(config, "base")
            command.upgrade(config, "0015_post_submit_correction")
            asyncio.run(_seed_artifact_prior_head(isolated_database_env, project_id))
            command.upgrade(config, "0016_artifact_domain")
            before = asyncio.run(
                _artifact_prior_head_project(isolated_database_env, project_id)
            )
            artifact_before = asyncio.run(
                _seed_and_fetch_0016_artifact(isolated_database_env, artifact_id)
            )

            command.upgrade(config, "0017_api_controls")
            after = asyncio.run(
                _artifact_prior_head_project(isolated_database_env, project_id)
            )
            artifact_after = asyncio.run(
                _fetch_0016_artifact(isolated_database_env, artifact_id)
            )
            schema = asyncio.run(_api_rate_control_schema(isolated_database_env))
            asyncio.run(_assert_api_rate_control_guards(isolated_database_env, digest))

            with pytest.raises(RuntimeError, match="non-empty API rate controls"):
                command.downgrade(config, "0016_artifact_domain")

            asyncio.run(_clear_api_rate_controls(isolated_database_env))
            inserted = threading.Event()
            release_insert = threading.Event()
            downgrade_started = threading.Event()

            def guarded_downgrade() -> None:
                downgrade_started.set()
                command.downgrade(config, "0016_artifact_domain")

            with ThreadPoolExecutor(max_workers=2) as pool:
                insert_future = pool.submit(
                    asyncio.run,
                    _insert_rate_control_until_released(
                        isolated_database_env,
                        digest,
                        inserted,
                        release_insert,
                    ),
                )
                assert inserted.wait(timeout=5)
                downgrade_future = pool.submit(guarded_downgrade)
                assert downgrade_started.wait(timeout=5)
                time.sleep(0.2)
                assert downgrade_future.done() is False
                release_insert.set()
                insert_future.result(timeout=5)
                with pytest.raises(RuntimeError, match="non-empty API rate controls"):
                    downgrade_future.result(timeout=5)

            refused_state = asyncio.run(_api_rate_control_state(isolated_database_env))
            asyncio.run(_clear_api_rate_controls(isolated_database_env))
            command.downgrade(config, "0016_artifact_domain")
            downgraded_state = asyncio.run(
                _api_rate_control_state(isolated_database_env)
            )
            command.upgrade(config, "0017_api_controls")
        finally:
            asyncio.run(_clear_api_rate_controls(isolated_database_env))
            asyncio.run(_truncate_artifact_foundation(isolated_database_env))
            command.downgrade(config, "base")

    assert after == before
    assert artifact_after == artifact_before
    assert schema == {
        "columns": {
            "control_scope:character varying:NO",
            "key_digest:bytea:NO",
            "window_started_at:timestamp with time zone:NO",
            "window_expires_at:timestamp with time zone:NO",
            "request_count:bigint:NO",
            "updated_at:timestamp with time zone:NO",
        },
        "constraints": {
            "pk_api_rate_control_counters",
            "ck_api_rate_control_counters_scope_token",
            "ck_api_rate_control_counters_digest_length",
            "ck_api_rate_control_counters_request_count",
            "ck_api_rate_control_counters_window_order",
        },
        "indexes": {
            "pk_api_rate_control_counters",
            "ix_api_rate_control_counters_window_expires_at",
        },
    }
    assert refused_state == {
        "revision": "0017_api_controls",
        "table_exists": True,
        "row_count": 1,
    }
    assert downgraded_state == {
        "revision": "0016_artifact_domain",
        "table_exists": False,
        "row_count": None,
    }


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


async def _seed_artifact_prior_head(database_url: str, project_id: str) -> None:
    """Seed one representative legacy row at the previous migration head."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into projects (id, name, slug, status)
                    values (:id, 'Prior artifact project', :slug, 'draft')
                    """
                ),
                {"id": project_id, "slug": f"prior-artifact-{project_id}"},
            )
    finally:
        await engine.dispose()


async def _seed_artifact_prior_head_runtime_rows(
    database_url: str,
    ids: dict[str, str],
) -> None:
    """Seed representative runtime rows valid at the 0015 migration head."""
    snapshot_id = ids["snapshot"]
    submission_policy_id = ids["submission_policy"]
    effective_policy_id = ids["effective_policy"]
    pre_submit_policy_id = ids["pre_submit_policy"]
    review_policy_id = ids["review_policy"]
    revision_policy_id = ids["revision_policy"]
    payment_policy_id = ids["payment_policy"]
    snapshot_hash = f"sha256:{'a' * 64}"
    submission_policy_hash = f"sha256:{'b' * 64}"
    effective_policy_hash = f"sha256:{'c' * 64}"
    pre_submit_bundle_hash = f"sha256:{'d' * 64}"
    post_submit_policy_hash = f"sha256:{'e' * 64}"
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into projects (id, name, slug, status)
                    values (:id, 'Artifact runtime project', :slug, 'active')
                    """
                ),
                {"id": ids["project"], "slug": f"artifact-runtime-{ids['project']}"},
            )
            await connection.execute(
                text(
                    """
                    insert into project_guides (
                        id, project_id, version, status, content_markdown,
                        created_by, approved_by
                    )
                    values (
                        :id, :project_id, 'v1', 'active', '# Artifact runtime guide',
                        'artifact-migration-test', 'artifact-migration-test'
                    )
                    """
                ),
                {"id": ids["guide"], "project_id": ids["project"]},
            )
            await connection.execute(
                text(
                    """
                    insert into guide_source_snapshots (
                        id, project_id, guide_id, guide_version,
                        manifest_schema_version, manifest_json, bundle_hash, captured_by
                    )
                    values (
                        :id, :project_id, :guide_id, 'v1', '1', '{}'::json,
                        :bundle_hash, 'artifact-migration-test'
                    )
                    """
                ),
                {
                    "id": snapshot_id,
                    "project_id": ids["project"],
                    "guide_id": ids["guide"],
                    "bundle_hash": snapshot_hash,
                },
            )
            await connection.execute(
                text(
                    """
                    insert into submission_artifact_policies (
                        id, project_id, guide_id, guide_version,
                        source_snapshot_id, source_snapshot_hash, policy_version,
                        lifecycle_status, policy_body, policy_hash, derivation_source,
                        source_material_refs, created_by, approved_by_role,
                        approved_by_actor, approved_at
                    )
                    values (
                        :id, :project_id, :guide_id, 'v1', :snapshot_id,
                        :snapshot_hash, 'v1', 'approved', '{}'::json, :policy_hash,
                        'migration_test', '[]'::json, 'artifact-migration-test',
                        'admin', 'artifact-migration-test', now()
                    )
                    """
                ),
                {
                    "id": submission_policy_id,
                    "project_id": ids["project"],
                    "guide_id": ids["guide"],
                    "snapshot_id": snapshot_id,
                    "snapshot_hash": snapshot_hash,
                    "policy_hash": submission_policy_hash,
                },
            )
            await connection.execute(
                text(
                    """
                    insert into effective_project_submission_artifact_policies (
                        id, project_id, guide_id, guide_version,
                        source_snapshot_id, source_snapshot_hash,
                        submission_artifact_policy_id, submission_artifact_policy_hash,
                        lifecycle_status, merge_algorithm_version, effective_policy,
                        effective_policy_hash, created_by
                    )
                    values (
                        :id, :project_id, :guide_id, 'v1', :snapshot_id,
                        :snapshot_hash, :submission_policy_id, :submission_policy_hash,
                        'approved', '1', '{}'::json, :effective_policy_hash,
                        'artifact-migration-test'
                    )
                    """
                ),
                {
                    "id": effective_policy_id,
                    "project_id": ids["project"],
                    "guide_id": ids["guide"],
                    "snapshot_id": snapshot_id,
                    "snapshot_hash": snapshot_hash,
                    "submission_policy_id": submission_policy_id,
                    "submission_policy_hash": submission_policy_hash,
                    "effective_policy_hash": effective_policy_hash,
                },
            )
            await connection.execute(
                text(
                    """
                    insert into pre_submit_checker_policies (
                        id, project_id, guide_id, guide_version,
                        source_snapshot_id, source_snapshot_hash, effective_policy_id,
                        effective_policy_hash, lifecycle_status, compiler_version,
                        compiled_bundle, compiled_bundle_hash, checker_names,
                        checker_configs, created_by
                    )
                    values (
                        :id, :project_id, :guide_id, 'v1', :snapshot_id,
                        :snapshot_hash, :effective_policy_id, :effective_policy_hash,
                        'compiled', '1', '{}'::json, :bundle_hash, '[]'::json,
                        '{}'::json, 'artifact-migration-test'
                    )
                    """
                ),
                {
                    "id": pre_submit_policy_id,
                    "project_id": ids["project"],
                    "guide_id": ids["guide"],
                    "snapshot_id": snapshot_id,
                    "snapshot_hash": snapshot_hash,
                    "effective_policy_id": effective_policy_id,
                    "effective_policy_hash": effective_policy_hash,
                    "bundle_hash": pre_submit_bundle_hash,
                },
            )
            await connection.execute(
                text(
                    """
                    insert into checker_policies (
                        id, project_id, guide_id, guide_version,
                        source_snapshot_id, source_snapshot_hash, effective_policy_id,
                        effective_policy_hash, pre_submit_checker_policy_id,
                        pre_submit_checker_bundle_hash, required_checkers,
                        warning_checkers, blocking_severities, policy_hash, policy_body,
                        lifecycle_status, approved_by_role, approved_by_actor,
                        approved_at, created_by
                    )
                    values (
                        :id, :project_id, :guide_id, 'v1', :snapshot_id,
                        :snapshot_hash, :effective_policy_id, :effective_policy_hash,
                        :pre_submit_policy_id, :pre_submit_bundle_hash,
                        '["artifact_integrity"]'::json, '[]'::json, '["high"]'::json,
                        :policy_hash, '{}'::json, 'approved', 'admin',
                        'artifact-migration-test', now(), 'artifact-migration-test'
                    )
                    """
                ),
                {
                    "id": ids["policy"],
                    "project_id": ids["project"],
                    "guide_id": ids["guide"],
                    "snapshot_id": snapshot_id,
                    "snapshot_hash": snapshot_hash,
                    "effective_policy_id": effective_policy_id,
                    "effective_policy_hash": effective_policy_hash,
                    "pre_submit_policy_id": pre_submit_policy_id,
                    "pre_submit_bundle_hash": pre_submit_bundle_hash,
                    "policy_hash": post_submit_policy_hash,
                },
            )
            await _seed_pre_provenance_policies_without_checker(
                connection,
                ids["project"],
                review_policy_id,
                revision_policy_id,
                payment_policy_id,
            )
            lock_params = {
                "project_id": ids["project"],
                "post_policy_id": ids["policy"],
                "post_policy_hash": post_submit_policy_hash,
                "snapshot_id": snapshot_id,
                "snapshot_hash": snapshot_hash,
                "effective_policy_id": effective_policy_id,
                "effective_policy_hash": effective_policy_hash,
                "pre_submit_policy_id": pre_submit_policy_id,
                "pre_submit_bundle_hash": pre_submit_bundle_hash,
            }
            await connection.execute(
                text(
                    """
                    insert into workstream_tasks (
                        id, project_id, locked_guide_version,
                        locked_post_submit_checker_policy_id,
                        locked_post_submit_checker_policy_version,
                        locked_post_submit_checker_policy_hash,
                        locked_post_submit_checker_policy_body,
                        locked_review_policy_version, locked_revision_policy_version,
                        locked_payment_policy_version, locked_guide_source_snapshot_id,
                        locked_guide_source_snapshot_hash,
                        locked_effective_project_submission_artifact_policy_id,
                        locked_effective_project_submission_artifact_policy_hash,
                        locked_pre_submit_checker_policy_id,
                        locked_pre_submit_checker_bundle_hash, source_type, title,
                        description, skill_tags, status, created_by
                    )
                    values (
                        :id, :project_id, 'v1', :post_policy_id, 'v1',
                        :post_policy_hash, '{}'::json, 'v1', 'v1', 'v1',
                        :snapshot_id, :snapshot_hash, :effective_policy_id,
                        :effective_policy_hash, :pre_submit_policy_id,
                        :pre_submit_bundle_hash, 'manual', 'Artifact runtime task',
                        'Representative task at migration 0015.', '[]'::json,
                        'in_progress', 'artifact-migration-test'
                    )
                    """
                ),
                {"id": ids["task"], **lock_params},
            )
            await connection.execute(
                text(
                    """
                    insert into submissions (
                        id, task_id, worker_id, version, status, summary,
                        package_hash, artifact_hash_manifest, worker_attestation,
                        locked_guide_version, locked_post_submit_checker_policy_id,
                        locked_post_submit_checker_policy_version,
                        locked_post_submit_checker_policy_hash,
                        locked_post_submit_checker_policy_body,
                        locked_review_policy_version, locked_revision_policy_version,
                        locked_payment_policy_version, locked_guide_source_snapshot_id,
                        locked_guide_source_snapshot_hash,
                        locked_effective_project_submission_artifact_policy_id,
                        locked_effective_project_submission_artifact_policy_hash,
                        locked_pre_submit_checker_policy_id,
                        locked_pre_submit_checker_bundle_hash
                    )
                    values (
                        :id, :task_id, 'artifact-worker', 1, 'submitted',
                        'Representative submission at migration 0015.',
                        'sha256:artifact-package', '[]'::json,
                        'artifact migration attestation', 'v1', :post_policy_id,
                        'v1', :post_policy_hash, '{}'::json, 'v1', 'v1', 'v1',
                        :snapshot_id, :snapshot_hash, :effective_policy_id,
                        :effective_policy_hash, :pre_submit_policy_id,
                        :pre_submit_bundle_hash
                    )
                    """
                ),
                {"id": ids["submission"], "task_id": ids["task"], **lock_params},
            )
            await connection.execute(
                text(
                    """
                    insert into checker_runs (
                        id, task_id, submission_id, submission_version,
                        trigger_source, status, routing_recommendation, outcome_source,
                        triggered_by, triggered_by_subject, triggered_by_issuer,
                        trigger_auth_source, attempt_number, is_current_for_submission,
                        locked_guide_version, locked_post_submit_checker_policy_id,
                        locked_post_submit_checker_policy_version,
                        locked_post_submit_checker_policy_hash,
                        locked_post_submit_checker_policy_body,
                        locked_review_policy_version, locked_revision_policy_version,
                        locked_payment_policy_version, package_hash,
                        artifact_hash_manifest, artifact_manifest_hash, passed_count,
                        warning_count, failed_count, blocking_count
                    )
                    values (
                        :id, :task_id, :submission_id, 1, 'submission_lock',
                        'completed', 'allow_review', 'auto_checker',
                        'artifact-migration-test', 'artifact-migration-test',
                        'flow-test', 'flow', 1, true, 'v1', :post_policy_id, 'v1',
                        :post_policy_hash, '{}'::json, 'v1', 'v1', 'v1',
                        'sha256:artifact-package', '[]'::json,
                        'sha256:artifact-manifest', 1, 0, 0, 0
                    )
                    """
                ),
                {
                    "id": ids["run"],
                    "task_id": ids["task"],
                    "submission_id": ids["submission"],
                    **lock_params,
                },
            )
    finally:
        await engine.dispose()


async def _seed_pre_provenance_policies_without_checker(
    connection,
    project_id: str,
    review_policy_id: str,
    revision_policy_id: str,
    payment_policy_id: str,
) -> None:
    """Seed the non-checker guide policies needed by a locked task."""
    await connection.execute(
        text(
            """
            insert into review_policies (
                id, project_id, guide_version, requires_second_review,
                allowed_decisions, minimum_finding_fields
            ) values (
                :id, :project_id, 'v1', false,
                '["accept", "needs_revision", "reject"]'::json, '[]'::json
            )
            """
        ),
        {"id": review_policy_id, "project_id": project_id},
    )
    await connection.execute(
        text(
            """
            insert into revision_policies (
                id, project_id, guide_version, max_revision_rounds,
                revision_deadline_hours, auto_reject_after_limit,
                allowed_resubmission_states
            ) values (
                :id, :project_id, 'v1', 7, 48, true, '["needs_revision"]'::json
            )
            """
        ),
        {"id": revision_policy_id, "project_id": project_id},
    )
    await connection.execute(
        text(
            """
            insert into payment_policies (
                id, project_id, guide_version, base_amount, currency, payout_type
            ) values (:id, :project_id, 'v1', 25.00, 'USD', 'fixed')
            """
        ),
        {"id": payment_policy_id, "project_id": project_id},
    )


async def _artifact_prior_head_project(database_url: str, project_id: str) -> dict[str, str]:
    """Return exact prior-head project values for migration comparison."""
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            row = (
                await connection.execute(
                    text("select id, name, slug, status from projects where id = :id"),
                    {"id": project_id},
                )
            ).mappings().one()
            return dict(row)
    finally:
        await engine.dispose()


async def _artifact_prior_head_runtime_rows(
    database_url: str, ids: dict[str, str]
) -> dict[str, dict]:
    """Return every column from representative populated 0015 domain rows."""
    table_ids = {
        "projects": ids["project"],
        "project_guides": ids["guide"],
        "guide_source_snapshots": ids["snapshot"],
        "submission_artifact_policies": ids["submission_policy"],
        "effective_project_submission_artifact_policies": ids["effective_policy"],
        "pre_submit_checker_policies": ids["pre_submit_policy"],
        "checker_policies": ids["policy"],
        "review_policies": ids["review_policy"],
        "revision_policies": ids["revision_policy"],
        "payment_policies": ids["payment_policy"],
        "workstream_tasks": ids["task"],
        "submissions": ids["submission"],
        "checker_runs": ids["run"],
    }
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            rows: dict[str, dict] = {}
            for table_name, row_id in table_ids.items():
                value = await connection.scalar(
                    text(
                        f"select row_to_json(selected) from "
                        f"(select * from {table_name} where id = :id) selected"
                    ),
                    {"id": row_id},
                )
                assert isinstance(value, dict)
                rows[table_name] = value
            return rows
    finally:
        await engine.dispose()


async def _artifact_table_counts(database_url: str) -> dict[str, int]:
    """Return row counts for every additive artifact table."""
    tables = (
        "artifact_upload_sessions",
        "artifact_upload_items",
        "artifact_contents",
        "artifact_bindings",
        "artifact_replicas",
        "artifact_operation_receipts",
    )
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            counts: dict[str, int] = {}
            for table in tables:
                count = await connection.scalar(text(f"select count(*) from {table}"))
                counts[table] = int(count or 0)
            return counts
    finally:
        await engine.dispose()


async def _assert_artifact_fact_guards(database_url: str, ids: dict[str, str]) -> None:
    """Exercise digest and immutable-row guards directly in PostgreSQL."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    insert into projects (id, name, slug, status)
                    values (:project_id, 'Artifact guards', :slug, 'draft')
                    """
                ),
                {"project_id": ids["project"], "slug": f"guards-{ids['project']}"},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_contents (id, sha256, byte_count)
                    values (:content_id, :sha256, 0)
                    """
                ),
                {"content_id": ids["content"], "sha256": "sha256:" + "0" * 64},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_upload_sessions (
                        id, actor_id, project_id, permitted_roles, state,
                        maximum_bytes, current_bytes, reserved_bytes,
                        maximum_items, current_items, reserved_items, expires_at, cas_version
                    ) values (
                        :id, 'actor', :project, '[]'::json, 'open',
                        8, 0, 4, 1, 0, 1, now() + interval '1 hour', 0
                    )
                    """
                ),
                {"id": ids["session"], "project": ids["project"]},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_upload_items (
                        id, session_id, logical_role, display_name, reserved_bytes,
                        idempotency_key, request_digest, state, cas_version
                    ) values (
                        :id, :session, 'packet', 'packet.bin', 4,
                        'idem', :digest, 'reserved', 0
                    )
                    """
                ),
                {"id": ids["item"], "session": ids["session"], "digest": "sha256:" + "1" * 64},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_replicas (
                        id, content_id, adapter, provider_artifact_id,
                        verification_state, retention_state, availability_state, integrity_state
                    ) values (
                        :id, :content, 'local', 'artifact-provider-id',
                        'pending', 'unretained', 'available', 'valid'
                    )
                    """
                ),
                {"id": ids["replica"], "content": ids["content"]},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_operation_receipts (
                        id, upload_item_id, replica_id, adapter, service_principal,
                        operation, idempotency_key, request_digest, response_digest,
                        provider_receipt_id, provider_operation_reference, outcome, attempt_number,
                        correlation_id, provider_recorded_at, details
                    ) values (
                        :id, :item, :replica, 'local', 'workstream.artifact',
                        'store', 'idem', :request_digest, :response_digest,
                        'provider-receipt', 'provider-operation', 'stored', 1,
                        'correlation', now(), '{}'::json
                    )
                    """
                ),
                {
                    "id": ids["receipt"],
                    "item": ids["item"],
                    "replica": ids["replica"],
                    "request_digest": "sha256:" + "1" * 64,
                    "response_digest": "sha256:" + "2" * 64,
                },
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_bindings (
                        id, content_id, project_id, resource_type, resource_id,
                        logical_role, scope_version, actor_id, attribution_type
                    ) values (
                        :id, :content, :project, 'submission', 'submission-1',
                        'packet', 1, 'actor', 'submitted_by'
                    )
                    """
                ),
                {"id": ids["binding"], "content": ids["content"], "project": ids["project"]},
            )
            await connection.execute(
                text(
                    """
                    insert into artifact_bindings (
                        id, content_id, project_id, resource_type, resource_id,
                        logical_role, scope_version, actor_id, attribution_type,
                        supersedes_binding_id
                    ) values (
                        :id, :content, :project, 'submission', 'submission-1',
                        'packet', 2, 'actor', 'submitted_by', :predecessor
                    )
                    """
                ),
                {
                    "id": ids["binding_v2"],
                    "content": ids["content"],
                    "project": ids["project"],
                    "predecessor": ids["binding"],
                },
            )
        with pytest.raises(DBAPIError):
            async with engine.begin() as connection:
                await connection.execute(
                    text("update artifact_contents set byte_count = 1 where id = :id"),
                    {"id": ids["content"]},
                )
        with pytest.raises(IntegrityError):
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        insert into artifact_contents (id, sha256, byte_count)
                        values (:id, 'SHA256:INVALID', 1)
                        """
                    ),
                    {"id": str(uuid4())},
                )
        failing_statements = (
            (
                "update artifact_upload_sessions set state = 'unknown' where id = :id",
                {"id": ids["session"]},
            ),
            (
                "update artifact_upload_sessions set current_bytes = -1 where id = :id",
                {"id": ids["session"]},
            ),
            (
                "update artifact_upload_sessions set state = 'sealed' where id = :id",
                {"id": ids["session"]},
            ),
            (
                "update artifact_upload_sessions set reserved_bytes = 9 where id = :id",
                {"id": ids["session"]},
            ),
            (
                "update artifact_upload_items set state = 'unknown' where id = :id",
                {"id": ids["item"]},
            ),
            (
                "update artifact_upload_items set reserved_bytes = -1 where id = :id",
                {"id": ids["item"]},
            ),
            (
                "update artifact_upload_items set cas_version = -1 where id = :id",
                {"id": ids["item"]},
            ),
            (
                "update artifact_upload_items set content_id = :content, "
                "provider_operation_reference = 'op' where id = :id",
                {"id": ids["item"], "content": ids["content"]},
            ),
            (
                "update artifact_upload_items set state = 'ready' where id = :id",
                {"id": ids["item"]},
            ),
            (
                "update artifact_replicas set verification_state = 'trusted' where id = :id",
                {"id": ids["replica"]},
            ),
            (
                "update artifact_replicas set retention_state = 'held' where id = :id",
                {"id": ids["replica"]},
            ),
            (
                "update artifact_replicas set availability_state = 'online' where id = :id",
                {"id": ids["replica"]},
            ),
            (
                "update artifact_replicas set integrity_state = 'trusted' where id = :id",
                {"id": ids["replica"]},
            ),
            (
                "update artifact_operation_receipts set operation = 'copy' where id = :id",
                {"id": ids["receipt"]},
            ),
            (
                "update artifact_operation_receipts set attempt_number = 0 where id = :id",
                {"id": ids["receipt"]},
            ),
            (
                "update artifact_operation_receipts set outcome = 'verified' where id = :id",
                {"id": ids["receipt"]},
            ),
            (
                "delete from artifact_operation_receipts where id = :id",
                {"id": ids["receipt"]},
            ),
            (
                "update artifact_bindings set logical_role = 'other' where id = :id",
                {"id": ids["binding"]},
            ),
            (
                "delete from artifact_bindings where id = :id",
                {"id": ids["binding_v2"]},
            ),
        )
        for statement, parameters in failing_statements:
            with pytest.raises(DBAPIError):
                async with engine.begin() as connection:
                    await connection.execute(text(statement), parameters)

        duplicate_statements = (
            (
                "insert into artifact_contents (id, sha256, byte_count) "
                "select :new_id, sha256, byte_count from artifact_contents where id = :id",
                {"new_id": str(uuid4()), "id": ids["content"]},
            ),
            (
                "insert into artifact_upload_items "
                "(id, session_id, logical_role, display_name, reserved_bytes, "
                "idempotency_key, request_digest, state, cas_version) "
                "select :new_id, session_id, logical_role, display_name, reserved_bytes, "
                "idempotency_key, request_digest, state, cas_version "
                "from artifact_upload_items where id = :id",
                {"new_id": str(uuid4()), "id": ids["item"]},
            ),
            (
                "insert into artifact_replicas "
                "(id, content_id, adapter, provider_artifact_id, verification_state, "
                "retention_state, availability_state, integrity_state) "
                "select :new_id, content_id, adapter, provider_artifact_id, "
                "verification_state, retention_state, availability_state, integrity_state "
                "from artifact_replicas where id = :id",
                {"new_id": str(uuid4()), "id": ids["replica"]},
            ),
            (
                "insert into artifact_operation_receipts "
                "(id, upload_item_id, replica_id, adapter, service_principal, operation, "
                "idempotency_key, request_digest, response_digest, provider_receipt_id, "
                "provider_operation_reference, outcome, attempt_number, correlation_id, "
                "provider_recorded_at, details) "
                "select :new_id, upload_item_id, replica_id, adapter, service_principal, "
                "operation, idempotency_key, request_digest, response_digest, "
                "provider_receipt_id || '-duplicate', provider_operation_reference, outcome, "
                "attempt_number, correlation_id || '-duplicate', provider_recorded_at, details "
                "from artifact_operation_receipts where id = :id",
                {"new_id": str(uuid4()), "id": ids["receipt"]},
            ),
        )
        for statement, parameters in duplicate_statements:
            with pytest.raises(IntegrityError):
                async with engine.begin() as connection:
                    await connection.execute(text(statement), parameters)

        with pytest.raises(IntegrityError):
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        insert into artifact_operation_receipts (
                            id, replica_id, adapter, service_principal, operation,
                            idempotency_key, request_digest, response_digest,
                            provider_receipt_id, provider_operation_reference, outcome, attempt_number,
                            correlation_id, retention_reference, retention_class,
                            provider_recorded_at, details
                        ) values (
                            :id, :replica, 'local', 'workstream.artifact', 'retain',
                            'retain-without-owner', :request_digest, :response_digest,
                            'provider-receipt-retain', 'provider-retain', 'retained', 1,
                            'correlation-retain',
                            'reference', 'standard', now(), '{}'::json
                        )
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "replica": ids["replica"],
                        "request_digest": "sha256:" + "3" * 64,
                        "response_digest": "sha256:" + "4" * 64,
                    },
                )
        with pytest.raises(DBAPIError):
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        insert into artifact_bindings (
                            id, content_id, project_id, resource_type, resource_id,
                            logical_role, scope_version, actor_id, attribution_type,
                            supersedes_binding_id
                        ) values (
                            :id, :content, :project, 'submission', 'submission-1',
                            'packet', 3, 'actor', 'submitted_by', :wrong_predecessor
                        )
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "content": ids["content"],
                        "project": ids["project"],
                        "wrong_predecessor": ids["binding"],
                    },
                )
    finally:
        await engine.dispose()


async def _truncate_artifact_foundation(database_url: str) -> None:
    """Clear artifact rows after guarded-downgrade assertions."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    truncate table
                        artifact_operation_receipts,
                        artifact_replicas,
                        artifact_bindings,
                        artifact_upload_items,
                        artifact_contents,
                        artifact_upload_sessions
                    cascade
                    """
                )
            )
    finally:
        await engine.dispose()


async def _api_rate_control_schema(database_url: str) -> dict[str, set[str]]:
    """Return the exact public schema contract for the rate table."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            columns = (
                await connection.execute(
                    text(
                        "select column_name, data_type, is_nullable "
                        "from information_schema.columns "
                        "where table_schema = 'public' "
                        "and table_name = 'api_rate_control_counters'"
                    )
                )
            ).all()
            constraints = (
                await connection.execute(
                    text(
                        "select conname from pg_constraint "
                        "where conrelid = 'api_rate_control_counters'::regclass"
                    )
                )
            ).scalars()
            indexes = (
                await connection.execute(
                    text(
                        "select indexname from pg_indexes "
                        "where schemaname = 'public' "
                        "and tablename = 'api_rate_control_counters'"
                    )
                )
            ).scalars()
            return {
                "columns": {
                    f"{row.column_name}:{row.data_type}:{row.is_nullable}"
                    for row in columns
                },
                "constraints": set(constraints),
                "indexes": set(indexes),
            }
    finally:
        await engine.dispose()


async def _seed_and_fetch_0016_artifact(
    database_url: str, artifact_id: str
) -> dict[str, object]:
    """Seed one representative 0016 row and return its exact persisted value."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "insert into artifact_contents "
                    "(id, sha256, byte_count, media_type, normalized_display_name) "
                    "values (:id, :sha256, 17, 'text/plain', 'rate-migration.txt')"
                ),
                {"id": artifact_id, "sha256": "sha256:" + "7" * 64},
            )
    finally:
        await engine.dispose()
    return await _fetch_0016_artifact(database_url, artifact_id)


async def _fetch_0016_artifact(
    database_url: str, artifact_id: str
) -> dict[str, object]:
    """Fetch the representative 0016 artifact-domain row."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            row = (
                await connection.execute(
                    text(
                        "select id, sha256, byte_count, media_type, "
                        "normalized_display_name from artifact_contents where id = :id"
                    ),
                    {"id": artifact_id},
                )
            ).mappings().one()
            return dict(row)
    finally:
        await engine.dispose()


async def _insert_rate_control_until_released(
    database_url: str,
    digest: bytes,
    inserted: threading.Event,
    release: threading.Event,
) -> None:
    """Hold an uncommitted writer until the downgrade is waiting on its lock."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "insert into api_rate_control_counters "
                    "(control_scope, key_digest, window_started_at, window_expires_at, "
                    "request_count, updated_at) values "
                    "('first_access', :digest, statement_timestamp(), "
                    "statement_timestamp() + interval '1 minute', 1, statement_timestamp())"
                ),
                {"digest": digest},
            )
            inserted.set()
            assert await asyncio.to_thread(release.wait, 5)
    finally:
        await engine.dispose()


async def _assert_api_rate_control_guards(database_url: str, digest: bytes) -> None:
    """Insert one valid counter and reject every malformed direct variant."""
    engine = create_async_engine(database_url)
    insert_sql = text(
        "insert into api_rate_control_counters "
        "(control_scope, key_digest, window_started_at, window_expires_at, "
        "request_count, updated_at) values "
        "(:scope, :digest, statement_timestamp(), "
        "statement_timestamp() + make_interval(secs => :seconds), "
        ":count, statement_timestamp())"
    )
    valid = {
        "scope": "first_access",
        "digest": digest,
        "seconds": 60,
        "count": 1,
    }
    try:
        async with engine.begin() as connection:
            await connection.execute(insert_sql, valid)

        invalid = [
            {**valid, "scope": "caller_supplied", "digest": bytes([1]) * 32},
            {**valid, "digest": bytes(31)},
            {**valid, "digest": bytes([2]) * 32, "count": 0},
            {**valid, "digest": bytes([3]) * 32, "seconds": 0},
            valid,
        ]
        for values in invalid:
            with pytest.raises(IntegrityError):
                async with engine.begin() as connection:
                    await connection.execute(insert_sql, values)
    finally:
        await engine.dispose()


async def _api_rate_control_state(database_url: str) -> dict[str, object]:
    """Return revision, table existence, and row count after migration actions."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            revision = await connection.scalar(text("select version_num from alembic_version"))
            exists = await connection.scalar(
                text("select to_regclass('public.api_rate_control_counters') is not null")
            )
            count = None
            if exists:
                count = await connection.scalar(
                    text("select count(*) from api_rate_control_counters")
                )
            return {
                "revision": revision,
                "table_exists": exists,
                "row_count": count,
            }
    finally:
        await engine.dispose()


async def _clear_api_rate_controls(database_url: str) -> None:
    """Clear rate rows only when the migration table exists."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            exists = await connection.scalar(
                text("select to_regclass('public.api_rate_control_counters') is not null")
            )
            if exists:
                await connection.execute(text("delete from api_rate_control_counters"))
    finally:
        await engine.dispose()
