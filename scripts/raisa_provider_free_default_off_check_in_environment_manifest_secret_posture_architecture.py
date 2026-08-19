"""Validate the provider-free check-in environment/secret-posture architecture."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
CONTRACT_SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"
MANIFEST_SCHEMA_PATH = CONTRACT_DIR / "environment-manifest.schema.json"

EXPECTED_SOURCE_HEAD = "8cc8aaf5e52c97ed46b868afb0ee6038eb1cf40a"
EXPECTED_SUCCESSOR_RESOLUTION_SOURCE = "f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e"
EXPECTED_READINESS_SOURCE = "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"
EXPECTED_ADMISSION_ARCHITECTURE_SOURCE = "752b521c59f5b44bf46de0cf776a33ac74b8134d"
EXPECTED_UNMOUNTED_KERNEL_SOURCE = "4204ec6348abb0f92b1a30314699d4a469fa860a"
EXPECTED_CONTRACT_DIGEST = "57b595df5b6074e5cf24821220752603a636b985701dfbc48c0e99eebe4a7f39"
EXPECTED_MANIFEST_SCHEMA_DIGEST = "786cab3b19231c391d281cf36568b4206fe5f11b2a2ac51469f0996c3e718e88"
EXPECTED_SOURCES = {
    "docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md": "630e2745beebeff184ed48861c86607f3b68d764ad023f688c63a509f3d13edb",
    "orchestration/continuity/raisa-provider-free-clockwork-governed-check-in-successor-resolution/successor-resolution-report.md": "75812ad3f92fd7c8cbaa5b50492b6ac23edadfd0cc06bd312870fb19a18ebbab",
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md": "3bffad89188d3f700e769d4d39301b8f440d763b21d0e4b7c64fe67354ed78ba",
    "orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review/admission-readiness-review-report.md": "81a4a92e4f1f7e539282a646d59474420309f2f93785fe2c007e413ef26c297f",
    "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-plan.md": "744c175e18b335bd02cb954e501d6d3cba99744b052fc1e34f4b445050cc49f1",
    "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md": "ce520b9d8c90d46aba7cb5bad1c59585d508d9d1849051443c5a45e1a68371ab",
    "orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json": "505120968572362a7df8d67ab1d95947ed1cd467df0fbc520aca73a704755ba9",
    "orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/architecture-report.md": "9223066a1a0d7413c449e3916953f0b0e04db389fc5fea8c3283eb917471a807",
    "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-plan.md": "4a2a4a4c0a926a8362f62d77353ae88b3dc2778cf4701a56282915c88cb37391",
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/contract.json": "d2ad88328ae235d5eb5b059087c7bf896b37d93f66f8ed379677c7a5ba1c1511",
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/kernel-rehearsal-report.md": "10f619e4dc8d10228e1f4c06c0b98da45cf073a2715fdbde30cf1aa0fb3f0233",
    ".env.example": "c31eb51ece0eb8c49054ce76cee57f64c21fe50c07da716c112cdc01627a0ebe",
    "app/config.py": "f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e",
    "app/database.py": "2da2b2d584391755a1d9de4e274d59f05dcc24b6b5a3737a35efae49c7f6b117",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    "orchestration/api_spine_programme.md": "5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946",
}
EXPECTED_SLOT_IDS = [
    "database_connection_credential",
    "application_token_signing_key",
    "admission_snapshot_verification_key",
]
EXPECTED_MANIFEST_FIELDS = [
    "schema_version",
    "manifest_id",
    "environment",
    "admission_snapshot_generation",
    "authority_git_object",
    "practice_scope_reference",
    "runtime_role",
    "secret_references",
    "rotation_evidence",
    "break_glass",
    "issued_at",
    "expires_at",
]
EXPECTED_EVALUATOR_STEPS = [
    "validate_closed_shape_digest_full_git_resolution_environment_uniqueness_and_freshness",
    "deny_unless_one_exact_logical_and_physical_runtime_role_binding_exists",
    "deny_unless_three_distinct_ordered_secret_reference_slots_exist",
    "deny_unless_role_and_rotation_evidence_bind_the_same_environment_and_snapshot_generation",
    "deny_if_any_evidence_is_missing_invalid_stale_self_verified_or_wrong_version",
    "deny_unless_break_glass_state_is_exactly_inactive",
    "return_typed_evidence_gate_reading_without_admission_or_command_capability",
]
FORBIDDEN_SECRET_FIELDS = {
    "value",
    "secret_value",
    "password",
    "token",
    "private_key",
    "database_url",
    "connection_url",
    "environment_value",
    "secret_material_sha256",
    "secret_fingerprint",
    "secret_manager_endpoint",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_contract_schema() -> dict[str, Any]:
    return _load(CONTRACT_SCHEMA_PATH)


def load_manifest_schema() -> dict[str, Any]:
    return _load(MANIFEST_SCHEMA_PATH)


def _canonical_json_digest(value: dict[str, Any]) -> str:
    material = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _canonical_source_digest(path: Path) -> str:
    text = path.read_bytes().decode("utf-8", errors="strict")
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise ValueError("bare CR is forbidden")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_errors(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bindings = {row["path"]: row["sha256"] for row in packet["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        return ["source_bindings_mismatch"]
    for relative_path, expected_digest in EXPECTED_SOURCES.items():
        source = ROOT / relative_path
        if not source.is_file():
            errors.append(f"source_missing:{relative_path}")
            continue
        try:
            actual = _canonical_source_digest(source)
        except (UnicodeDecodeError, ValueError):
            errors.append(f"source_not_canonical_utf8_lf:{relative_path}")
            continue
        if actual != expected_digest:
            errors.append(f"source_hash_mismatch:{relative_path}")
    return errors


def semantic_errors(
    packet: dict[str, Any],
    *,
    verify_source_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    expected_ids = {
        "source_head": EXPECTED_SOURCE_HEAD,
        "accepted_successor_resolution_source": EXPECTED_SUCCESSOR_RESOLUTION_SOURCE,
        "accepted_readiness_source": EXPECTED_READINESS_SOURCE,
        "accepted_admission_architecture_source": EXPECTED_ADMISSION_ARCHITECTURE_SOURCE,
        "accepted_unmounted_kernel_source": EXPECTED_UNMOUNTED_KERNEL_SOURCE,
    }
    for field, expected in expected_ids.items():
        if packet.get(field) != expected:
            errors.append(f"{field}_mismatch")
    if _canonical_json_digest(packet) != EXPECTED_CONTRACT_DIGEST:
        errors.append("contract_digest_mismatch")
    if verify_source_files:
        errors.extend(source_errors(packet))

    posture = packet["current_posture"]
    zero_count_fields = (
        "ordinary_admission_records_present",
        "environment_manifest_instances_present",
        "selected_practice_bindings_present",
        "ordinary_runtime_role_bindings_present",
        "secret_reference_bindings_present",
        "operational_evidence_artifacts_present",
    )
    if any(posture[field] != 0 for field in zero_count_fields):
        errors.append("canonical_population_not_empty")
    if (
        posture["feature_default"]
        or posture["synthetic_allowlist_default"] != []
        or posture["secret_values_supplied"]
        or posture["database_opened"]
        or posture["product_configuration_changed"]
        or posture["ordinary_practice_enabled"]
        or posture["default_result"] != "deny_environment_manifest_absent"
    ):
        errors.append("current_posture_not_default_denied")

    manifest = packet["manifest_profile"]
    if manifest["normalized_schema_sha256"] != EXPECTED_MANIFEST_SCHEMA_DIGEST:
        errors.append("manifest_schema_digest_mismatch")
    if _canonical_source_digest(MANIFEST_SCHEMA_PATH) != EXPECTED_MANIFEST_SCHEMA_DIGEST:
        errors.append("manifest_schema_file_digest_mismatch")
    if manifest["required_top_level_fields"] != EXPECTED_MANIFEST_FIELDS:
        errors.append("manifest_field_order_mismatch")
    if (
        manifest["canonical_instance_count"] != 0
        or manifest["full_git_object_pattern"] != "^[0-9a-f]{40}$"
        or manifest["unknown_fields_behavior"] != "deny"
        or manifest["missing_manifest_behavior"] != "deny"
        or manifest["multiple_current_manifests_behavior"] != "deny"
        or manifest["wrong_environment_behavior"] != "deny"
        or manifest["stale_manifest_behavior"]
        != "deny_without_last_known_good_fallback"
        or manifest["caller_selected_environment_or_practice_allowed"]
        or manifest["manifest_is_activation_authority"]
        or manifest["yaml_loader_implemented"]
    ):
        errors.append("manifest_fail_closed_profile_mismatch")

    role = packet["runtime_role_profile"]
    if (
        role["logical_role_id"] != "appointment_check_in_ordinary_runtime_v1"
        or not role["physical_role_identifier_is_non_secret"]
        or not role["non_owner_required"]
        or not role["nobypassrls_required"]
        or role["product_relation_ownership_allowed"]
        or not role["cross_tenant_denial_attestation_required"]
        or not role["exact_environment_attestation_required"]
        or role["role_created"]
        or role["role_attested"]
        or role["database_connected"]
    ):
        errors.append("runtime_role_profile_open_or_claimed")

    secret = packet["secret_reference_profile"]
    if [row["slot_id"] for row in secret["ordered_slots"]] != EXPECTED_SLOT_IDS:
        errors.append("secret_slot_order_mismatch")
    if set(secret["forbidden_field_names"]) != FORBIDDEN_SECRET_FIELDS:
        errors.append("forbidden_secret_field_set_mismatch")
    if any(row["value_allowed"] for row in secret["ordered_slots"]):
        errors.append("secret_value_allowed")
    if (
        not secret["reference_only"]
        or secret["slot_reference_reuse_allowed"]
        or secret["key_identifier_reuse_across_slots_allowed"]
        or secret["cross_environment_reference_reuse_allowed"]
        or secret["repository_secret_value_allowed"]
        or secret["provider_endpoint_allowed"]
        or secret["current_reference_count"] != 0
    ):
        errors.append("secret_reference_boundary_open")

    rotation = packet["rotation_evidence_profile"]
    if rotation["ordered_slot_ids"] != EXPECTED_SLOT_IDS:
        errors.append("rotation_slot_order_mismatch")
    if (
        not rotation["required_for_each_slot"]
        or not rotation["artifact_digest_is_evidence_digest_not_secret_material_digest"]
        or not rotation["full_git_object_required"]
        or not rotation["independent_verifier_required"]
        or rotation["self_verified_evidence_allowed"]
        or not rotation["fresh_until_must_follow_observed_at"]
        or not rotation["evaluation_time_must_precede_fresh_until"]
        or not rotation[
            "exact_environment_slot_key_version_and_generation_binding_required"
        ]
        or rotation["old_key_evidence_reuse_allowed"]
        or rotation["current_evidence_count"] != 0
    ):
        errors.append("rotation_evidence_boundary_open")

    break_glass = packet["break_glass_profile"]
    authority_fields = (
        "may_supply_secret",
        "may_skip_rotation",
        "may_attest_role",
        "may_activate_practice",
        "may_clear_global_kill_switch",
        "may_grant_command_authority",
        "automatic_clear_allowed",
        "last_known_good_fallback",
    )
    if (
        break_glass["mode"] != "deny_only"
        or break_glass["states"] != ["inactive", "engaged_deny", "retired"]
        or break_glass["only_state_allowing_evidence_evaluation_to_continue"]
        != "inactive"
        or break_glass["missing_or_malformed_behavior"] != "deny"
        or any(break_glass[field] for field in authority_fields)
        or not break_glass["recovery_requires_new_manifest_generation"]
        or not break_glass["recovery_requires_fresh_independent_evidence"]
    ):
        errors.append("break_glass_not_deny_only")

    evaluator = packet["evidence_gate_evaluator"]
    if evaluator["ordered_steps"] != EXPECTED_EVALUATOR_STEPS:
        errors.append("evaluator_order_mismatch")
    capability_fields = (
        "may_admit_ordinary_practice",
        "may_execute_check_in",
        "may_connect_database",
        "may_resolve_secret",
        "may_create_or_change_role",
        "may_mutate_product_configuration",
    )
    if (
        evaluator["canonical_current_outcome"] != "denied"
        or evaluator["canonical_current_reason_code"] != "manifest_absent"
        or any(evaluator[field] for field in capability_fields)
    ):
        errors.append("evidence_evaluator_has_authority")

    operational = packet["operational_evidence_boundary"]
    if (
        not operational["architecture_portion_frozen"]
        or operational["environment_and_secret_posture_operational_gap_closed"]
        or operational["tenant_runtime_role_operational_gap_closed"]
        or operational["rollback_and_unknown_commit_operational_gap_closed"]
        or operational["this_contract_is_operational_evidence"]
        or operational[
            "authored_synthetic_substitution_for_ordinary_evidence_allowed"
        ]
        or operational["missing_or_unproved_behavior"] != "deny"
    ):
        errors.append("operational_evidence_claim_open")

    clockwork = packet["clockwork_boundary"]
    if (
        clockwork["governance_clockwork_status"] != "accepted_live_single_owner"
        or clockwork["closeout_projection_owner"] != "clockwork"
        or not clockwork["full_git_objects_are_machine_resolved"]
        or clockwork["manual_git_abbreviation_accepted"]
        or clockwork["deepseek_native_harness_occupied_for_this_tranche"]
        or clockwork["deepseek_broker_has_product_or_secret_authority"]
        or clockwork["workflow_receipt_is_operational_or_product_authority"]
    ):
        errors.append("clockwork_or_broker_boundary_open")
    if any(packet["closed_boundaries"].values()):
        errors.append("closed_boundary_open")
    successor = packet["successor"]
    if (
        successor["operation_id"]
        != "raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal"
        or successor["authorized_now"]
        or successor["ordinary_enablement_authorized"]
        or successor["production_or_live_secret_authorized"]
    ):
        errors.append("successor_authority_open")
    return sorted(set(errors))


def validate_contract(
    packet: dict[str, Any],
    *,
    verify_source_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    for error in Draft202012Validator(load_contract_schema()).iter_errors(packet):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"schema:{location}:{error.validator}")
    if errors:
        return sorted(set(errors))
    return semantic_errors(packet, verify_source_files=verify_source_files)


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone_required")
    return parsed.astimezone(timezone.utc)


def _forbidden_key_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = (*prefix, key)
            if key.lower() in FORBIDDEN_SECRET_FIELDS:
                paths.append("/".join(str(part) for part in path))
            paths.extend(_forbidden_key_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_forbidden_key_paths(child, (*prefix, index)))
    return paths


def manifest_errors(value: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["manifest_object_required"]
    validator = Draft202012Validator(
        load_manifest_schema(),
        format_checker=FormatChecker(),
    )
    for error in validator.iter_errors(value):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"manifest_schema:{location}:{error.validator}")
    forbidden = _forbidden_key_paths(value)
    errors.extend(f"forbidden_secret_field:{path}" for path in forbidden)
    if errors:
        return sorted(set(errors))

    environment_id = value["environment"]["identifier"]
    generation = value["admission_snapshot_generation"]
    references = value["secret_references"]
    rotations = value["rotation_evidence"]
    if [row["slot_id"] for row in references] != EXPECTED_SLOT_IDS:
        errors.append("secret_slot_order_mismatch")
    if [row["slot_id"] for row in rotations] != EXPECTED_SLOT_IDS:
        errors.append("rotation_slot_order_mismatch")
    secret_refs = [row["secret_reference"] for row in references]
    key_ids = [row["key_id"] for row in references]
    if len(set(secret_refs)) != len(secret_refs):
        errors.append("secret_reference_reused")
    if len(set(key_ids)) != len(key_ids):
        errors.append("key_identifier_reused_across_slots")
    for reference, rotation in zip(references, rotations):
        if rotation["environment_identifier"] != environment_id:
            errors.append(f"rotation_environment_mismatch:{rotation['slot_id']}")
        if rotation["admission_snapshot_generation"] != generation:
            errors.append(f"rotation_generation_mismatch:{rotation['slot_id']}")
        if rotation["key_id"] != reference["key_id"]:
            errors.append(f"rotation_key_mismatch:{rotation['slot_id']}")
        if rotation["version"] != reference["version"]:
            errors.append(f"rotation_version_mismatch:{rotation['slot_id']}")
        if rotation["evidence_reference"] != reference["rotation_evidence_reference"]:
            errors.append(f"rotation_reference_mismatch:{rotation['slot_id']}")
        if rotation["independent_verifier_reference"] == rotation["evidence_reference"]:
            errors.append(f"rotation_self_verified:{rotation['slot_id']}")
        try:
            if _parse_time(rotation["fresh_until"]) <= _parse_time(
                rotation["observed_at"]
            ):
                errors.append(f"rotation_freshness_order_invalid:{rotation['slot_id']}")
        except ValueError:
            errors.append(f"rotation_time_invalid:{rotation['slot_id']}")
    try:
        if _parse_time(value["expires_at"]) <= _parse_time(value["issued_at"]):
            errors.append("manifest_freshness_order_invalid")
    except ValueError:
        errors.append("manifest_time_invalid")
    return sorted(set(errors))


def evaluate_manifest(
    value: object | None,
    *,
    evaluation_time: str,
    operational_evidence_verified: bool,
) -> dict[str, Any]:
    if value is None:
        return {"outcome": "denied", "reason_code": "manifest_absent"}
    errors = manifest_errors(value)
    if errors:
        return {"outcome": "denied", "reason_code": "manifest_invalid"}
    assert isinstance(value, dict)
    now = _parse_time(evaluation_time)
    if now >= _parse_time(value["expires_at"]) or any(
        now >= _parse_time(row["fresh_until"])
        for row in value["rotation_evidence"]
    ):
        return {"outcome": "denied", "reason_code": "manifest_stale"}
    if value["break_glass"]["state"] != "inactive":
        return {"outcome": "denied", "reason_code": "break_glass_not_inactive"}
    if not operational_evidence_verified:
        return {"outcome": "denied", "reason_code": "role_evidence_invalid"}
    return {"outcome": "satisfied", "reason_code": "evidence_gate_satisfied"}


def build_synthetic_manifest() -> dict[str, Any]:
    environment_id = "env:authored-synthetic-check-in"
    generation = 1
    slots = [
        ("database_connection_credential", "database-credential-v1"),
        ("application_token_signing_key", "application-signing-v1"),
        ("admission_snapshot_verification_key", "admission-verification-v1"),
    ]
    references = []
    rotations = []
    for index, (slot_id, key_id) in enumerate(slots, start=1):
        evidence_reference = f"evidence-ref:synthetic/{slot_id}/rotation-1"
        references.append(
            {
                "slot_id": slot_id,
                "provider_namespace": "authored-synthetic-store",
                "secret_reference": f"secret-ref:synthetic/{slot_id}/v1",
                "key_id": key_id,
                "version": "v1",
                "rotation_policy_reference": "policy-ref:check-in/rotation-v1",
                "rotation_evidence_reference": evidence_reference,
            }
        )
        rotations.append(
            {
                "slot_id": slot_id,
                "evidence_reference": evidence_reference,
                "artifact_sha256": str(index) * 64,
                "authority_git_object": EXPECTED_SOURCE_HEAD,
                "environment_identifier": environment_id,
                "admission_snapshot_generation": generation,
                "key_id": key_id,
                "version": "v1",
                "rotation_sequence": 1,
                "observed_at": "2026-08-19T00:00:00+10:00",
                "fresh_until": "2026-12-01T00:00:00+10:00",
                "independent_verifier_reference": (
                    f"evidence-ref:synthetic/{slot_id}/independent-verifier-1"
                ),
            }
        )
    return {
        "schema_version": "emr4.check-in-ordinary-environment-manifest.v1",
        "manifest_id": "check-in-env-manifest:authored-synthetic-v1",
        "environment": {
            "class": "test",
            "identifier": environment_id,
        },
        "admission_snapshot_generation": generation,
        "authority_git_object": EXPECTED_SOURCE_HEAD,
        "practice_scope_reference": "practice-ref:authored-synthetic-only",
        "runtime_role": {
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": "check_in_synthetic_runtime",
            "credential_secret_slot_id": "database_connection_credential",
            "non_owner_required": True,
            "nobypassrls_required": True,
            "product_relation_ownership_allowed": False,
            "tenant_attestation_reference": (
                "evidence-ref:synthetic/runtime-role/tenant-attestation-v1"
            ),
        },
        "secret_references": references,
        "rotation_evidence": rotations,
        "break_glass": {
            "mode": "deny_only",
            "state": "inactive",
            "evidence_reference": "evidence-ref:synthetic/break-glass/inactive-v1",
            "bypass_allowed": False,
            "secret_injection_allowed": False,
            "automatic_clear_allowed": False,
        },
        "issued_at": "2026-08-19T00:00:00+10:00",
        "expires_at": "2026-12-01T00:00:00+10:00",
    }


def _scalar_paths(value: Any, prefix: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _scalar_paths(child, (*prefix, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _scalar_paths(child, (*prefix, index))
    elif isinstance(value, (str, bool, int, float)) or value is None:
        yield prefix


def _get(value: Any, path: tuple[Any, ...]) -> Any:
    cursor = value
    for part in path:
        cursor = cursor[part]
    return cursor


def _set(value: Any, path: tuple[Any, ...], replacement: Any) -> None:
    cursor = value
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement


def _mutated_scalar(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value + "__hostile"
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    return "hostile_not_null"


def hostile_contract_mutations(
    packet: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []
    for index, path in enumerate(_scalar_paths(packet)):
        candidate = copy.deepcopy(packet)
        _set(candidate, path, _mutated_scalar(_get(candidate, path)))
        label = "/".join(str(part) for part in path)
        mutations.append((f"scalar_{index:03d}:{label}", candidate))
    for key in (
        "current_posture",
        "manifest_profile",
        "runtime_role_profile",
        "secret_reference_profile",
        "rotation_evidence_profile",
        "break_glass_profile",
        "evidence_gate_evaluator",
        "operational_evidence_boundary",
        "clockwork_boundary",
        "closed_boundaries",
        "successor",
    ):
        candidate = copy.deepcopy(packet)
        candidate[key]["unexpected_hostile_field"] = True
        mutations.append((f"extra_field:{key}", candidate))
    return mutations


def hostile_manifest_mutations() -> list[tuple[str, dict[str, Any]]]:
    base = build_synthetic_manifest()
    mutations: list[tuple[str, dict[str, Any]]] = []
    for key in EXPECTED_MANIFEST_FIELDS:
        candidate = copy.deepcopy(base)
        del candidate[key]
        mutations.append((f"missing_top_level:{key}", candidate))
    candidate = copy.deepcopy(base)
    candidate["unexpected"] = True
    mutations.append(("unexpected_top_level", candidate))
    candidate = copy.deepcopy(base)
    candidate["authority_git_object"] = EXPECTED_SOURCE_HEAD[:7]
    mutations.append(("abbreviated_manifest_git_object", candidate))
    for field in sorted(FORBIDDEN_SECRET_FIELDS):
        candidate = copy.deepcopy(base)
        candidate["secret_references"][0][field] = "forbidden"
        mutations.append((f"raw_secret_field:{field}", candidate))
    for index in range(3):
        candidate = copy.deepcopy(base)
        del candidate["secret_references"][index]
        mutations.append((f"missing_secret_slot:{index}", candidate))
        candidate = copy.deepcopy(base)
        del candidate["rotation_evidence"][index]
        mutations.append((f"missing_rotation_slot:{index}", candidate))
    for first, second in ((0, 1), (0, 2), (1, 2)):
        candidate = copy.deepcopy(base)
        candidate["secret_references"][second]["secret_reference"] = candidate[
            "secret_references"
        ][first]["secret_reference"]
        mutations.append((f"duplicate_secret_reference:{first}:{second}", candidate))
        candidate = copy.deepcopy(base)
        candidate["secret_references"][second]["key_id"] = candidate[
            "secret_references"
        ][first]["key_id"]
        candidate["rotation_evidence"][second]["key_id"] = candidate[
            "secret_references"
        ][first]["key_id"]
        mutations.append((f"duplicate_key_id:{first}:{second}", candidate))
    candidate = copy.deepcopy(base)
    candidate["secret_references"][0], candidate["secret_references"][1] = (
        candidate["secret_references"][1],
        candidate["secret_references"][0],
    )
    mutations.append(("secret_slot_reordered", candidate))
    candidate = copy.deepcopy(base)
    candidate["rotation_evidence"][0], candidate["rotation_evidence"][1] = (
        candidate["rotation_evidence"][1],
        candidate["rotation_evidence"][0],
    )
    mutations.append(("rotation_slot_reordered", candidate))
    for index in range(3):
        for field, replacement in (
            ("environment_identifier", "env:wrong-environment"),
            ("admission_snapshot_generation", 2),
            ("key_id", "wrong-key-id"),
            ("version", "v2"),
            ("evidence_reference", "evidence-ref:synthetic/wrong-evidence"),
            ("authority_git_object", EXPECTED_SOURCE_HEAD[:7]),
        ):
            candidate = copy.deepcopy(base)
            candidate["rotation_evidence"][index][field] = replacement
            mutations.append((f"rotation_mismatch:{index}:{field}", candidate))
        candidate = copy.deepcopy(base)
        rotation = candidate["rotation_evidence"][index]
        rotation["independent_verifier_reference"] = rotation["evidence_reference"]
        mutations.append((f"rotation_self_verified:{index}", candidate))
        candidate = copy.deepcopy(base)
        candidate["rotation_evidence"][index]["fresh_until"] = (
            "2026-08-18T00:00:00+10:00"
        )
        mutations.append((f"rotation_freshness_inverted:{index}", candidate))
    for state in ("engaged_deny", "retired"):
        candidate = copy.deepcopy(base)
        candidate["break_glass"]["state"] = state
        mutations.append((f"break_glass:{state}", candidate))
    for field in ("bypass_allowed", "secret_injection_allowed", "automatic_clear_allowed"):
        candidate = copy.deepcopy(base)
        candidate["break_glass"][field] = True
        mutations.append((f"break_glass_authority:{field}", candidate))
    candidate = copy.deepcopy(base)
    candidate["expires_at"] = "2026-08-18T00:00:00+10:00"
    mutations.append(("manifest_freshness_inverted", candidate))
    return mutations


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_contract() if packet is None else packet
    errors = validate_contract(packet, verify_source_files=True)
    contract_mutants = hostile_contract_mutations(packet)
    contract_escapes = [
        name for name, mutant in contract_mutants if not validate_contract(mutant)
    ]
    synthetic = build_synthetic_manifest()
    synthetic_errors = manifest_errors(synthetic)
    if synthetic_errors:
        errors.extend(f"synthetic_manifest:{reason}" for reason in synthetic_errors)
    denied_without_evidence = evaluate_manifest(
        synthetic,
        evaluation_time="2026-08-20T00:00:00+10:00",
        operational_evidence_verified=False,
    )
    shape_only_satisfaction = evaluate_manifest(
        synthetic,
        evaluation_time="2026-08-20T00:00:00+10:00",
        operational_evidence_verified=True,
    )
    if denied_without_evidence != {
        "outcome": "denied",
        "reason_code": "role_evidence_invalid",
    }:
        errors.append("missing_operational_evidence_did_not_deny")
    if shape_only_satisfaction != {
        "outcome": "satisfied",
        "reason_code": "evidence_gate_satisfied",
    }:
        errors.append("synthetic_shape_did_not_reach_bounded_gate_reading")
    manifest_mutants = hostile_manifest_mutations()
    manifest_escapes = []
    for name, mutant in manifest_mutants:
        outcome = evaluate_manifest(
            mutant,
            evaluation_time="2026-08-20T00:00:00+10:00",
            operational_evidence_verified=True,
        )
        if outcome == {
            "outcome": "satisfied",
            "reason_code": "evidence_gate_satisfied",
        }:
            manifest_escapes.append(name)
    if contract_escapes:
        errors.append("hostile_contract_escape:" + ",".join(contract_escapes))
    if manifest_escapes:
        errors.append("hostile_manifest_escape:" + ",".join(manifest_escapes))
    return {
        "schema_version": "emr4.check-in-environment-manifest-secret-posture-architecture-report.v1",
        "status": "passed" if not errors else "failed",
        "reasons": sorted(set(errors)),
        "source_head": packet["source_head"],
        "source_binding_count": len(packet["source_bindings"]),
        "manifest_schema_sha256": _canonical_source_digest(MANIFEST_SCHEMA_PATH),
        "secret_slot_count": len(packet["secret_reference_profile"]["ordered_slots"]),
        "canonical_manifest_instance_count": packet["manifest_profile"]["canonical_instance_count"],
        "current_secret_reference_count": packet["secret_reference_profile"]["current_reference_count"],
        "current_rotation_evidence_count": packet["rotation_evidence_profile"]["current_evidence_count"],
        "contract_hostile_mutation_count": len(contract_mutants),
        "contract_hostile_mutation_escape_count": len(contract_escapes),
        "manifest_hostile_mutation_count": len(manifest_mutants),
        "manifest_hostile_mutation_escape_count": len(manifest_escapes),
        "missing_operational_evidence_outcome": denied_without_evidence,
        "bounded_synthetic_shape_outcome": shape_only_satisfaction,
        "ordinary_practice_enabled": packet["closed_boundaries"]["ordinary_practice_enabled"],
        "secret_value_used": packet["closed_boundaries"]["secret_or_key_value_created_read_or_written"],
        "database_or_role_used": packet["closed_boundaries"]["database_connected_or_role_created"],
        "product_or_configuration_changed": packet["closed_boundaries"]["product_source_or_configuration_changed"],
        "provider_or_network_used": packet["closed_boundaries"]["provider_or_network_used"],
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
