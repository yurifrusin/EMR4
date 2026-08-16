from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture
    as architecture,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-"
    "product-adapter-architecture-plan.md"
)

# The exact compact canonical private-receipt physical bytes: frozen six-field
# insertion order (appointment_id, status, status_reason_code,
# cancellation_reason, waiting_area_id, warning_codes), compact separators
# (",", ":"), literal UTF-8 and no whitespace.
CLEAN_RECEIPT_BYTES = (
    b'{"appointment_id":"3f3f3f3f-0000-0000-0000-000000000003",'
    b'"status":"Cancelled","status_reason_code":"PATIENT_CANCELLED",'
    b'"cancellation_reason":null,"waiting_area_id":null,"warning_codes":[]}'
)


def _canonical_bytes(receipt: dict) -> bytes:
    return json.dumps(
        receipt,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


ARCHITECTURE = (
    ROOT
    / "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-"
    "product-adapter-architecture.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-delete-confirm-response-"
    "compatibility-product-adapter-architecture-threat-model-delta.md"
)


@pytest.fixture(scope="module")
def contract() -> dict:
    return json.loads(architecture.CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def contract_schema() -> dict:
    return json.loads(architecture.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def evidence_schema() -> dict:
    return json.loads(architecture.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built_evidence() -> dict:
    return architecture.build_evidence()


@pytest.fixture(scope="module")
def committed_evidence() -> dict:
    return json.loads(architecture.EVIDENCE_PATH.read_text(encoding="utf-8"))


def _walk_objects(node):
    """Yield every dict in a JSON-like structure."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_objects(value)


def test_contract_is_closed_unmounted_and_not_implementation_authority(contract, contract_schema):
    architecture.validate_schema(contract, contract_schema)
    architecture.validate_contract_semantics(contract)
    assert contract["mode"] == "provider_free_unmounted_architecture_only"
    assert contract["schema_version"] == "raisa.delete_confirm_response_product_adapter_architecture.v1"
    assert contract["operation_id"] == "confirmAppointmentDeleteProposal"
    assert contract["route_family"] == "delete-confirm"
    assert contract["input_hash_mode"] == "strict_utf8_canonical_lf_reject_bare_cr_sha256"
    assert contract["authority_ingress"]["client_authority_fields"] == []
    assert contract["authority_ingress"]["effect_authority_before_physical_seam"] is False
    assert contract["admission"]["effect_authority"] is False
    assert contract["composition"]["route_local_fallback"] is False
    assert contract["composition"]["replay_effect_count"] == 0


def test_contract_schema_closes_every_object_with_additional_properties_false(contract_schema):
    for obj in _walk_objects(contract_schema):
        if obj.get("type") == "object":
            assert obj.get("additionalProperties") is False, obj.get("$id") or obj


def test_evidence_schema_closes_every_object_with_additional_properties_false(evidence_schema):
    for obj in _walk_objects(evidence_schema):
        if obj.get("type") == "object":
            assert obj.get("additionalProperties") is False, obj.get("$id") or obj


def test_all_fourteen_exact_source_hashes_pass(contract):
    observed = architecture.verify_source_bindings(contract)
    assert observed == architecture.EXPECTED_SOURCE_BINDINGS
    assert len(observed) == 14
    assert len(contract["input_bindings"]) == 14


def test_all_four_frozen_semantic_output_digests_pass():
    observed = architecture.verify_semantic_output_hashes()
    assert observed == architecture.EXPECTED_SEMANTIC_OUTPUT_HASHES
    assert len(observed) == 4


def test_precommit_receipt_records_the_four_frozen_digests():
    binding = architecture.verify_precommit_receipt_binding()
    assert binding["semantic_output_digests_recorded"] is True
    assert binding["bound_digest_count"] == 4


def test_source_commit_binding_is_exact():
    assert architecture.EXPECTED_SOURCE_COMMIT == "5aaed2a859c64062d40dd2fe1b419d48dcc5d821"


def test_private_receipt_is_six_fields_sole_persisted_authority(contract):
    receipt = contract["private_receipt"]
    assert receipt["schema_version"] == "appointment.delete_confirmation_private_receipt.v1"
    assert receipt["persistence_authority"] == "sole"
    assert receipt["canonical_field_order"] == [
        "appointment_id",
        "status",
        "status_reason_code",
        "cancellation_reason",
        "waiting_area_id",
        "warning_codes",
    ]
    assert receipt["status_constant"] == "Cancelled"
    assert receipt["waiting_area_constant"] is None
    assert receipt["warning_code_order"] == "sorted_unique"
    assert "patient" in receipt["forbidden_fields"]
    assert "practitioner" in receipt["forbidden_fields"]
    assert "appointment" in receipt["forbidden_fields"]
    assert "notes" in receipt["forbidden_fields"]


def test_public_projection_is_minimal_versioned_envelope(contract):
    projection = contract["public_projection"]
    assert projection["schema_version"] == "raisa.delete_confirm_public_envelope.v1"
    assert projection["receipt_schema_version"] == "appointment.delete_confirmation_receipt.v1"
    assert projection["source"] == "validated_private_receipt_bytes_only"
    assert projection["initial_and_replay_use_same_projection"] is True
    assert projection["current_appointment_read_for_response"] is False
    assert "appointment" in projection["forbidden_success_fields"]
    assert "live_projection" in projection["forbidden_success_fields"]
    assert "audit_event" in projection["forbidden_success_fields"]
    constants = projection["success_constants"]
    assert constants["intent"] == "confirm_delete_appointment"
    assert constants["safe"] is True
    assert constants["requires_confirmation"] is False
    assert constants["autonomy_tier"] == "confirmed_write"
    assert constants["blocks"] == []
    assert constants["audit_evidence"] == [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked",
    ]


def test_authority_ingress_is_server_owned_with_double_checks(contract):
    authority = contract["authority_ingress"]
    assert authority["server_owned_fields"] == [
        "practice_id",
        "actor_id",
        "actor_role",
        "authority_generation",
        "authenticated_session_reference",
    ]
    assert authority["client_authority_fields"] == []
    assert authority["capability_constant"] == "appointment.cancel.confirm"
    assert authority["capability_check_owner"] == "delete_confirm_locked_transaction"
    assert authority["current_authority_check_count"] == 2
    assert authority["command_session"] == "distinct_server_owned_close_after_use"
    assert authority["effect_authority_before_physical_seam"] is False


def test_double_admission_pre_command_and_locked(contract):
    admission = contract["admission"]
    assert "opaque_positive_source_version_binding" in admission["pre_command_checks"]
    assert "explicit_confirmation" in admission["pre_command_checks"]
    assert "idempotency_key_present" in admission["pre_command_checks"]
    assert "same_positive_source_version" in admission["locked_checks"]
    assert "status_not_cancelled" in admission["locked_checks"]
    assert "warning_acknowledgement" in admission["locked_checks"]
    assert admission["effect_authority"] is False
    assert len(admission["pre_command_checks"]) == 9
    assert len(admission["locked_checks"]) == 7


def test_one_physical_write_set_and_zero_replay_effects(contract):
    composition = contract["composition"]
    assert composition["transaction_factory"] == "delete_confirm_locked_transaction"
    assert composition["new_command_write_set"] == [
        "appointment_cancellation",
        "attributable_delete_audit",
        "complete_private_receipt",
    ]
    assert composition["replay_effect_count"] == 0
    assert composition["route_local_fallback"] is False


def test_outcome_mapping_is_closed_and_non_disclosing(contract):
    mapping = {tuple(entry["outcomes"]): entry for entry in contract["outcome_mapping"]}
    assert mapping[("committed", "replay")]["http_status"] == 200
    assert mapping[("proposal_stop", "admission_stop")]["http_status"] == 200
    assert mapping[("idempotency_key_missing", "idempotency_conflict")]["http_status"] == 409
    assert mapping[("current_authority_unavailable",)]["http_status"] == 403
    target = mapping[("target_unavailable", "cross_practice_target")]
    assert target["http_status"] == 404
    assert target["body"] == "indistinguishable_unavailable"
    partial = mapping[("in_progress_not_replayable", "legacy_receipt_not_replayable")]
    assert partial["http_status"] == 409
    assert partial["body"] == "no_partial_receipt"
    assert len(contract["outcome_mapping"]) == 7


def test_alias_convergence_and_raw_delete_isolation(contract):
    compatibility = contract["compatibility"]
    assert compatibility["future_canonical_path"] == "/appointments/proposals/delete/confirm"
    assert compatibility["future_hidden_alias"] == "/appointments/proposals/delete-confirm"
    assert compatibility["one_future_handler"] is True
    assert compatibility["one_public_envelope_version"] is True
    assert compatibility["raw_delete_path"] == "/appointments/{appointment_id}"
    assert compatibility["raw_delete_isolation"] == [
        "no_dedicated_adapter_import_or_call",
        "no_dedicated_capability_inheritance",
        "no_dedicated_receipt_or_replay_inheritance",
    ]


def test_claim_boundary_stays_architecture_only(contract):
    boundary = contract["claim_boundary"]
    assert "server_owned_authority_and_locked_readmission_design" in boundary["proves"]
    for claim in (
        "adapter_or_schema_implementation",
        "route_or_http_behavior",
        "database_execution",
        "capability_provisioning",
        "client_compatibility",
        "deployment_or_production",
    ):
        assert claim in boundary["does_not_prove"]
    assert "route_edit_mount_or_call" in contract["forbidden_surfaces"]


def test_all_hostile_mutations_fail_closed(built_evidence):
    hostile = built_evidence["hostile_mutations"]
    assert hostile["attempted"] >= 100
    assert hostile["attempted"] == 136
    assert hostile["rejected"] == hostile["attempted"]
    assert hostile["minimum_required"] == 100


def test_every_dpa_family_is_represented():
    names = {name for name, _ in architecture.hostile_mutations()}
    for family in architecture.HOSTILE_FAMILY_NAMES:
        assert any(family in name for name in names), family


def test_all_hostile_evidence_mutations_fail_closed(built_evidence, committed_evidence, evidence_schema):
    result = architecture.reject_hostile_evidence_mutations(
        committed_evidence, built_evidence, evidence_schema
    )
    assert result["attempted"] >= 20
    assert result["rejected"] == result["attempted"]


def test_committed_evidence_equals_fresh_builder_output(built_evidence, committed_evidence):
    assert committed_evidence == built_evidence
    assert committed_evidence["source_head"] == "5aaed2a859c64062d40dd2fe1b419d48dcc5d821"
    assert committed_evidence["contract_source_head"] == "f0c98682568784441991b080681f9beb3b9354c2"
    assert committed_evidence["architecture_facts"]["authority_ingress"]["current_authority_check_count"] == 2
    assert committed_evidence["architecture_facts"]["composition"]["replay_effect_count"] == 0
    assert committed_evidence["architecture_facts"]["private_receipt"]["canonical_field_count"] == 6
    assert committed_evidence["side_effects"]["route_calls"] == 0
    assert committed_evidence["side_effects"]["database_connections"] == 0
    assert committed_evidence["side_effects"]["provider_calls"] == 0
    assert committed_evidence["side_effects"]["network_calls"] == 0
    assert committed_evidence["side_effects"]["subprocess_calls"] == 0
    assert committed_evidence["side_effects"]["product_patient_records"] == 0


def test_verify_evidence_admits_the_frozen_evidence(built_evidence):
    admitted = architecture.verify_evidence()
    assert admitted == built_evidence


def test_evidence_schema_requires_complete_shape_and_closes_objects(evidence_schema):
    required = set(evidence_schema["required"])
    assert {
        "schema_version",
        "result",
        "source_head",
        "evidence_label",
        "input_hash_mode",
        "contract_source_head",
        "contract_fingerprint",
        "source_hashes",
        "semantic_output_hashes",
        "precommit_receipt",
        "architecture_facts",
        "hostile_mutations",
        "side_effects",
        "claim_boundary",
    } <= required
    for obj in _walk_objects(evidence_schema):
        if obj.get("type") == "object":
            assert obj.get("additionalProperties") is False


def test_public_envelope_is_deterministic_pure_projection_of_private_bytes():
    assert CLEAN_RECEIPT_BYTES == _canonical_bytes(
        {
            "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
            "status": "Cancelled",
            "status_reason_code": "PATIENT_CANCELLED",
            "cancellation_reason": None,
            "waiting_area_id": None,
            "warning_codes": [],
        }
    )
    first = architecture.project_public_envelope(CLEAN_RECEIPT_BYTES)
    second = architecture.project_public_envelope(CLEAN_RECEIPT_BYTES)
    assert first == second
    envelope = json.loads(first.decode("utf-8"))
    assert envelope["schema_version"] == "raisa.delete_confirm_public_envelope.v1"
    assert envelope["intent"] == "confirm_delete_appointment"
    assert envelope["safe"] is True
    assert envelope["requires_confirmation"] is False
    assert envelope["autonomy_tier"] == "confirmed_write"
    assert envelope["summary"] == "Confirmed delete proposal and cancelled one appointment."
    assert envelope["blocks"] == []
    assert envelope["audit_evidence"] == [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked",
    ]
    assert envelope["warnings"] == []
    assert envelope["receipt"]["schema_version"] == "appointment.delete_confirmation_receipt.v1"
    assert envelope["receipt"]["appointment_id"] == "3f3f3f3f-0000-0000-0000-000000000003"
    assert envelope["receipt"]["status"] == "Cancelled"
    assert envelope["receipt"]["waiting_area_id"] is None
    # No AppointmentOut / current-projection leakage in the public body.
    for forbidden in ("appointment", "patient", "practitioner", "notes", "reason", "audit_identity", "live_projection"):
        assert forbidden not in envelope


def test_public_envelope_rejects_appointment_out_leakage():
    receipt = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": [],
        "appointment": {"id": "3f3f3f3f-0000-0000-0000-000000000003"},
    }
    with pytest.raises(ValueError):
        architecture.project_public_envelope(json.dumps(receipt, sort_keys=True).encode("utf-8"))


def test_public_envelope_rejects_reordered_or_unknown_warning_codes():
    base = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": [],
    }
    unknown = dict(base, warning_codes=["unknown_code"])
    with pytest.raises(ValueError):
        architecture.project_public_envelope(json.dumps(unknown, sort_keys=True).encode("utf-8"))
    reordered = dict(base, warning_codes=["waiting_area_cleared", "waiting_area_cleared"])
    with pytest.raises(ValueError):
        architecture.project_public_envelope(json.dumps(reordered, sort_keys=True).encode("utf-8"))


def test_public_envelope_projects_registered_warnings():
    receipt = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": ["waiting_area_cleared"],
    }
    envelope = json.loads(
        architecture.project_public_envelope(_canonical_bytes(receipt)).decode("utf-8")
    )
    assert envelope["warnings"] == [
        {
            "code": "waiting_area_cleared",
            "severity": "warning",
            "message": "Deleting this appointment will remove the patient from the waiting area.",
        }
    ]


def test_clean_bytes_use_frozen_six_field_order():
    assert architecture.PRIVATE_RECEIPT_FIELDS == [
        "appointment_id",
        "status",
        "status_reason_code",
        "cancellation_reason",
        "waiting_area_id",
        "warning_codes",
    ]
    assert list(json.loads(CLEAN_RECEIPT_BYTES.decode("utf-8")).keys()) == (
        architecture.PRIVATE_RECEIPT_FIELDS
    )


def test_public_envelope_rejects_sorted_or_reordered_keys():
    receipt = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": [],
    }
    sorted_bytes = json.dumps(
        receipt, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    reordered = {
        "status": "Cancelled",
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": [],
    }
    reordered_bytes = _canonical_bytes(reordered)
    assert sorted_bytes != CLEAN_RECEIPT_BYTES
    assert reordered_bytes != CLEAN_RECEIPT_BYTES
    with pytest.raises(ValueError):
        architecture.project_public_envelope(sorted_bytes)
    with pytest.raises(ValueError):
        architecture.project_public_envelope(reordered_bytes)


def test_public_envelope_rejects_added_whitespace():
    receipt = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": None,
        "waiting_area_id": None,
        "warning_codes": [],
    }
    padded_bytes = json.dumps(
        receipt, ensure_ascii=False, allow_nan=False, indent=2
    ).encode("utf-8")
    spaced_bytes = json.dumps(
        receipt, ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    with pytest.raises(ValueError):
        architecture.project_public_envelope(padded_bytes)
    with pytest.raises(ValueError):
        architecture.project_public_envelope(spaced_bytes)


def test_public_envelope_rejects_crlf():
    crlf_bytes = (
        b'{"appointment_id":\r\n'
        b'"3f3f3f3f-0000-0000-0000-000000000003",\r\n'
        b'"status":\r\n"Cancelled",\r\n'
        b'"status_reason_code":\r\n"PATIENT_CANCELLED",\r\n'
        b'"cancellation_reason":\r\nnull,\r\n'
        b'"waiting_area_id":\r\nnull,\r\n'
        b'"warning_codes":\r\n[]}'
    )
    with pytest.raises(ValueError):
        architecture.project_public_envelope(crlf_bytes)


def test_public_envelope_rejects_duplicate_keys():
    duplicate_bytes = (
        b'{"appointment_id":"3f3f3f3f-0000-0000-0000-000000000003",'
        b'"appointment_id":"3f3f3f3f-0000-0000-0000-000000000003",'
        b'"status":"Cancelled","status_reason_code":"PATIENT_CANCELLED",'
        b'"cancellation_reason":null,"waiting_area_id":null,"warning_codes":[]}'
    )
    with pytest.raises(ValueError):
        architecture.project_public_envelope(duplicate_bytes)


def test_public_envelope_rejects_alternate_unicode_escaping():
    receipt = {
        "appointment_id": "3f3f3f3f-0000-0000-0000-000000000003",
        "status": "Cancelled",
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": "Cancelled: café",
        "waiting_area_id": None,
        "warning_codes": [],
    }
    canonical = _canonical_bytes(receipt)
    escaped = json.dumps(
        receipt, ensure_ascii=True, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
    assert escaped != canonical
    envelope = json.loads(
        architecture.project_public_envelope(canonical).decode("utf-8")
    )
    assert envelope["receipt"]["cancellation_reason"] == "Cancelled: café"
    with pytest.raises(ValueError):
        architecture.project_public_envelope(escaped)


def test_canonical_lf_hashing_rejects_bare_cr(tmp_path):
    path = tmp_path / "bare_cr.txt"
    path.write_bytes(b"line one\rline two\n")
    with pytest.raises(ValueError):
        architecture._canonical_lf_sha256(path)


def test_canonical_lf_hashing_rejects_non_utf8(tmp_path):
    path = tmp_path / "invalid_utf8.txt"
    path.write_bytes(b"\xff\xfe\x00\x01")
    with pytest.raises(ValueError):
        architecture._canonical_lf_sha256(path)


def test_canonical_lf_hashing_canonicalizes_crlf(tmp_path):
    path = tmp_path / "crlf.txt"
    path.write_bytes(b"a\r\nb\r\n")
    lf = tmp_path / "lf.txt"
    lf.write_bytes(b"a\nb\n")
    assert architecture._canonical_lf_sha256(path) == architecture._canonical_lf_sha256(lf)


def test_validator_imports_no_application_database_or_provider_modules():
    source = Path(architecture.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any(
        fragment in name
        for name in imported
        for fragment in ("sqlalchemy", "psycopg", "alembic", "google", "vertex", "requests", "httpx")
    )


def test_validator_has_no_executable_runtime_or_mutation_path():
    source = Path(architecture.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_fragments = (
        "write_text",
        "write_bytes",
        "subprocess",
        "Popen",
        "os.system",
        "os.remove",
        "os.rename",
        "shutil",
        "socket",
        "sqlalchemy",
        "psycopg",
        "alembic",
        "create_engine",
        "execute",
        "exec",
        "eval",
        "importlib",
        "requests",
        "httpx",
        "boto3",
        "paramiko",
        "getpass",
    )
    identifiers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
        elif isinstance(node, ast.Import):
            identifiers.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            identifiers.add(node.module)
            identifiers.update(alias.name for alias in node.names)
    for identifier in identifiers:
        for fragment in forbidden_fragments:
            assert fragment not in identifier, (fragment, identifier)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            assert name not in {"open", "exec", "eval"}, name


def test_plan_and_threat_model_freeze_the_architecture_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())
    architecture_doc = ARCHITECTURE.read_text(encoding="utf-8")
    compact_architecture = " ".join(architecture_doc.split())
    threat = THREAT.read_text(encoding="utf-8")
    compact_threat = " ".join(threat.split())
    for phrase in (
        "confirmAppointmentDeleteProposal",
        "delete-confirm",
        "appointment.cancel.confirm",
        "raisa.delete_confirm_public_envelope.v1",
        "appointment.delete_confirmation_receipt.v1",
        "six-field",
        "Provider-free unmounted delete-confirm response-compatibility and product-adapter architecture plan",
        "or open product runtime authority.",
    ):
        assert phrase in compact_plan, phrase
    for phrase in (
        "The stored six-field receipt is command truth.",
        "Neither is a current appointment read model.",
        "effect_authority",
        "No unlocked proposal read is promoted into effect authority.",
        "raisa.delete_proposal_version_binding.v1",
    ):
        assert phrase in compact_architecture, phrase
    for phrase in (
        "DPA-001",
        "DPA-005",
        "DPA-006",
        "DPA-007",
        "DPA-009",
        "DPA-010",
        "DPA-012",
        "DPA-013",
        "DPA-014",
    ):
        assert phrase in compact_threat, phrase
