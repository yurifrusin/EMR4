import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal"
)


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_contract_and_all_exact_sources_pass_before_environment_use() -> None:
    contract, source_hashes, mutations = rehearsal.verify_contract()

    assert contract["source_head"] == "455e41b8b9038813b290e67c43ce0b3190120988"
    assert (
        contract["accepted_environment_architecture_source"]
        == "a1f309a6d52d01f9866432f7e9abb8095788d023"
    )
    assert len(source_hashes) == 11
    assert mutations[0] >= 192
    assert mutations[0] == mutations[1]


def test_all_rehearsal_schemas_are_valid_draft_2020_12() -> None:
    for name in (
        "rehearsal-contract.schema.json",
        "tenant-role-attestation.schema.json",
        "rehearsal-evidence.schema.json",
    ):
        Draft202012Validator.check_schema(_load(name))


def test_manifest_fixture_is_closed_reference_only_and_hostile_mutations_deny() -> None:
    physical_role = "emr4_checkin_ord_0123456789abcdef"
    manifest = rehearsal.build_manifest(physical_role)

    rehearsal._validate_manifest(  # noqa: SLF001
        manifest, physical_role=physical_role, canonical=manifest
    )
    attempted, rejected = rehearsal.hostile_manifest_mutations_rejected(
        manifest, physical_role
    )

    assert attempted >= 64
    assert attempted == rejected
    assert manifest["runtime_role"]["logical_role_id"] == (
        "appointment_check_in_ordinary_runtime_v1"
    )
    assert manifest["authority_git_object"] == (
        "a1f309a6d52d01f9866432f7e9abb8095788d023"
    )
    assert [item["slot_id"] for item in manifest["secret_references"]] == [
        "database_connection_credential",
        "application_token_signing_key",
        "admission_snapshot_verification_key",
    ]
    assert "password" not in json.dumps(manifest).lower()


@pytest.mark.parametrize(
    "field",
    [
        "password",
        "database_url",
        "connection_url",
        "raw_output",
        "docker_environment",
        "container_name",
        "network_name",
    ],
)
def test_evidence_redaction_rejects_forbidden_fields(field: str) -> None:
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted({field: "authored-synthetic"})  # noqa: SLF001


def test_evidence_redaction_rejects_runtime_credentials_and_connection_urls() -> None:
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted(  # noqa: SLF001
            {"safe": "prefix-runtime-credential-suffix"},
            forbidden_values=("runtime-credential",),
        )
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted(  # noqa: SLF001
            {"safe": "postgresql://synthetic.invalid/db"}
        )


def test_contract_freezes_exact_scenarios_role_and_containment() -> None:
    contract = _load("rehearsal-contract.json")

    assert [
        (item["id"], item["kind"], item["expected"])
        for item in contract["scenarios"]
    ] == list(rehearsal.EXPECTED_SCENARIOS)
    role = contract["role_contract"]
    assert role["login"] is True
    assert role["superuser"] is False
    assert role["inherit"] is False
    assert role["bypass_rls"] is False
    assert role["owned_relations"] == 0
    containment = contract["containment_profile"]
    assert containment["pull_policy"] == "never"
    assert containment["network_internal"] is True
    assert containment["published_ports"] is False
    assert containment["admin_password_source"] == (
        "process_memory_random_32_bytes"
    )


def test_harness_imports_no_product_or_configuration_module() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal.py"
    ).read_text(encoding="utf-8")

    assert "from app" not in source
    assert "import app" not in source
    assert ".env" not in source
    assert "appointment_check_in_product_adapter" not in source
    assert "pull_policy" not in source or '"never"' in (
        BASE / "rehearsal-contract.json"
    ).read_text(encoding="utf-8")


def test_released_attestation_and_parent_evidence_are_closed_and_digest_bound() -> None:
    attestation = _load("tenant-role-attestation.json")
    evidence = _load("rehearsal-evidence.json")

    Draft202012Validator(_load("tenant-role-attestation.schema.json")).validate(
        attestation
    )
    Draft202012Validator(_load("rehearsal-evidence.schema.json")).validate(evidence)
    assert rehearsal._sha256(rehearsal._json_bytes(attestation)) == (  # noqa: SLF001
        evidence["attestation_sha256"]
    )
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations"]["escapes"] == 0
    assert evidence["cleanup"]["role_absent_before_teardown"] is True
    assert attestation["ordinary_admission_release_count"] == 0
    assert [item["id"] for item in attestation["scenarios"]] == [
        item[0] for item in rehearsal.EXPECTED_SCENARIOS
    ]
    serialized = json.dumps([attestation, evidence]).lower()
    for forbidden in (
        "password",
        "postgresql://",
        "connection_url",
        "raw_output",
        "container_name",
        "network_name",
        "docs/branding",
    ):
        assert forbidden not in serialized


def test_failure_evidence_is_sanitized() -> None:
    failure = rehearsal._failure_evidence(  # noqa: SLF001
        rehearsal.RehearsalFailure("scenario", "bounded_code", "sensitive-detail"),
        ["contract_verified"],
        {"status": "cleanup_verified", "role_absent_before_teardown": True},
    )

    serialized = json.dumps(failure)
    assert "sensitive-detail" not in serialized
    assert failure["failure"]["detail_sha256"] == rehearsal._sha256(  # noqa: SLF001
        "sensitive-detail"
    )
