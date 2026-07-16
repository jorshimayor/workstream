"""Behavior tests for fixed service-identity migration evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.actors.legacy_classification import database_binding_identifier
from app.modules.actors.service_identities import SERVICE_IDENTITY_VALUES, ServiceIdentity
from app.modules.actors.service_identity_migration import (
    MAPPING_FILE_ENV,
    ExistingServiceActorRow,
    ServiceActorIdentityMapping,
    ServiceActorIdentityMappingDraft,
    ServiceIdentityMappingError,
    build_envelope,
    build_report,
    canonical_draft_bytes,
    load_draft,
    load_envelope,
    load_migration_mapping,
    publish_envelope,
    source_row_set_sha256,
    validate_draft,
    verify_envelope,
)

ISSUER = "https://identity.example.test"
SUBJECT = "Opaque-Service-Subject"
ACTOR_ID = "11111111-1111-4111-8111-111111111111"
DATABASE_BINDING = database_binding_identifier("workstream", 16_384)
GENERATED_AT = "2026-07-16T12:00:00Z"


def source_row(
    *,
    actor_profile_id: str = ACTOR_ID,
    subject: str = SUBJECT,
) -> ExistingServiceActorRow:
    return ExistingServiceActorRow(
        actor_profile_id=actor_profile_id,
        issuer=ISSUER,
        subject=subject,
    )


def mapping(
    *,
    actor_profile_id: str = ACTOR_ID,
    subject: str = SUBJECT,
    service_identity: ServiceIdentity = ServiceIdentity.ARTIFACT_VERIFIER,
) -> ServiceActorIdentityMapping:
    return ServiceActorIdentityMapping(
        actor_profile_id=actor_profile_id,
        issuer=ISSUER,
        subject=subject,
        service_identity=service_identity,
    )


def draft(*rows: ServiceActorIdentityMapping) -> ServiceActorIdentityMappingDraft:
    return ServiceActorIdentityMappingDraft(schema_version=1, mappings=rows)


def envelope():
    return build_envelope(
        draft(mapping()),
        (source_row(),),
        database_binding=DATABASE_BINDING,
        generated_at=GENERATED_AT,
    )


def write_private_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")
    os.chmod(path, 0o600)


def test_fixed_service_identity_registry_is_exact() -> None:
    assert SERVICE_IDENTITY_VALUES == (
        "workstream.artifact.verifier",
        "workstream.artifact.put_resolver",
        "workstream.artifact.scheduler",
        "workstream.artifact.binding",
        "workstream.artifact.guide_reader",
        "workstream.artifact.materializer",
        "workstream.artifact.checker_output",
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("actor_profile_id", str(uuid4()).upper()),
        ("actor_profile_id", "not-a-uuid"),
        ("issuer", "http://identity.example.test"),
        ("issuer", "https://user@identity.example.test"),
        ("issuer", "https://identity.example.test?private=true"),
        ("subject", ""),
        ("subject", "   "),
        ("service_identity", "workstream.artifact.unknown"),
    ],
)
def test_mapping_rejects_noncanonical_or_unknown_values(field: str, value: str) -> None:
    payload = mapping().model_dump(mode="json")
    payload[field] = value
    with pytest.raises(ValidationError):
        ServiceActorIdentityMapping.model_validate(payload)


def test_draft_rejects_duplicate_profile_external_identity_and_fixed_identity() -> None:
    duplicate = mapping()
    with pytest.raises(ValidationError):
        draft(duplicate, duplicate)
    with pytest.raises(ValidationError):
        draft(
            duplicate,
            mapping(
                actor_profile_id="22222222-2222-4222-8222-222222222222",
                subject="Other-Subject",
            ),
        )


def test_exact_mapping_accepts_zero_subset_and_all_seven_rows() -> None:
    assert validate_draft(draft(), ()) == draft()
    assert validate_draft(draft(mapping()), (source_row(),)) == draft(mapping())
    source_rows = tuple(
        source_row(
            actor_profile_id=f"00000000-0000-4000-8000-{index:012d}",
            subject=f"subject-{index}",
        )
        for index in range(1, 8)
    )
    mapped_rows = tuple(
        mapping(
            actor_profile_id=row.actor_profile_id,
            subject=row.subject,
            service_identity=identity,
        )
        for row, identity in zip(source_rows, ServiceIdentity, strict=True)
    )
    assert validate_draft(draft(*mapped_rows), source_rows).mappings == mapped_rows


def test_exact_mapping_rejects_missing_extra_or_changed_private_source() -> None:
    with pytest.raises(ServiceIdentityMappingError, match="service_mapping_source_mismatch"):
        validate_draft(draft(), (source_row(),))
    with pytest.raises(ServiceIdentityMappingError, match="service_mapping_source_mismatch"):
        validate_draft(draft(mapping()), ())
    with pytest.raises(ServiceIdentityMappingError, match="service_mapping_source_mismatch"):
        validate_draft(draft(mapping(subject=SUBJECT.lower())), (source_row(),))


def test_envelope_has_stable_known_answer_and_detects_any_binding_drift() -> None:
    built = envelope()
    assert built.envelope_sha256 == "1ca678ece8ec42fbd119209b963e3d25b36fc9c60dc00e9788328d4ed517a2d8"
    assert verify_envelope(
        built,
        (source_row(),),
        database_binding=DATABASE_BINDING,
    ) == built
    with pytest.raises(ServiceIdentityMappingError, match="envelope_mismatch"):
        verify_envelope(
            built,
            (source_row(),),
            database_binding=database_binding_identifier("other", 16_384),
        )


def test_canonical_hashes_ignore_input_order() -> None:
    first = source_row()
    second = source_row(
        actor_profile_id="22222222-2222-4222-8222-222222222222",
        subject="Second",
    )
    first_mapping = mapping()
    second_mapping = mapping(
        actor_profile_id=second.actor_profile_id,
        subject=second.subject,
        service_identity=ServiceIdentity.ARTIFACT_PUT_RESOLVER,
    )
    assert source_row_set_sha256((first, second)) == source_row_set_sha256((second, first))
    assert canonical_draft_bytes(draft(first_mapping, second_mapping)) == canonical_draft_bytes(
        draft(second_mapping, first_mapping)
    )


@pytest.mark.parametrize(
    "payload",
    [
        b'{"schema_version":1,"schema_version":1,"mappings":[]}',
        b'{"schema_version":NaN,"mappings":[]}',
        b"{not-json}",
    ],
)
def test_private_loader_rejects_ambiguous_json_without_echo(tmp_path: Path, payload: bytes) -> None:
    path = tmp_path / "draft.json"
    path.write_bytes(payload)
    os.chmod(path, 0o600)
    with pytest.raises(ServiceIdentityMappingError) as captured:
        load_draft(path)
    assert SUBJECT not in str(captured.value)
    assert ISSUER not in str(captured.value)


def test_private_loader_rejects_open_permissions_and_symlink(tmp_path: Path) -> None:
    path = tmp_path / "draft.json"
    write_private_json(path, draft().model_dump(mode="json"))
    os.chmod(path, 0o644)
    with pytest.raises(ServiceIdentityMappingError, match="file_insecure"):
        load_draft(path)
    os.chmod(path, 0o600)
    link = tmp_path / "draft-link.json"
    link.symlink_to(path)
    with pytest.raises(ServiceIdentityMappingError, match="file_unavailable"):
        load_draft(link)


def test_publish_envelope_is_owner_only_reloadable_and_never_overwrites(tmp_path: Path) -> None:
    path = tmp_path / "envelope.json"
    publish_envelope(path, envelope())
    assert os.stat(path).st_mode & 0o777 == 0o600
    assert load_envelope(path) == envelope()
    with pytest.raises(ServiceIdentityMappingError, match="output_unavailable"):
        publish_envelope(path, envelope())


def test_migration_environment_is_required_only_for_existing_services(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(MAPPING_FILE_ENV, raising=False)
    assert load_migration_mapping((), database_binding=DATABASE_BINDING) is None
    with pytest.raises(ServiceIdentityMappingError, match="service_mapping_required"):
        load_migration_mapping((source_row(),), database_binding=DATABASE_BINDING)
    path = tmp_path / "envelope.json"
    publish_envelope(path, envelope())
    monkeypatch.setenv(MAPPING_FILE_ENV, str(path))
    assert load_migration_mapping(
        (source_row(),), database_binding=DATABASE_BINDING
    ) == envelope()
    with pytest.raises(ServiceIdentityMappingError, match="service_mapping_not_required"):
        load_migration_mapping((), database_binding=DATABASE_BINDING)


def test_report_contains_only_counts_and_non_secret_digests() -> None:
    snapshot = type("Snapshot", (), {"rows": (source_row(),), "database_binding": DATABASE_BINDING})
    report = build_report(snapshot, draft(mapping()), envelope=envelope())
    serialized = report.model_dump_json()
    assert report.mapped_count == 1
    assert ACTOR_ID not in serialized
    assert SUBJECT not in serialized
    assert ISSUER not in serialized
