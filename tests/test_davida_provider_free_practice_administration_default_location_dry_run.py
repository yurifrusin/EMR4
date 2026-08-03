"""Regression tests for Davida's default-location dry-run proposal."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.schemas.practice_administration_default_location_proposal import (
    ALLOWED_OPERATIONS,
    DefaultLocationProposalCandidate,
    DefaultLocationProposalResultAdapter,
    OPERATION,
    REJECTION_REASONS,
)
from app.services.practice.practice_administration_default_location_dry_run import (
    PROPOSAL_AUTHORITY_CEILING,
    dry_run_default_location_proposal,
)
from scripts.davida_provider_free_practice_administration_default_location_dry_run_acceptance import (
    _candidate,
    _canonical,
    _json_clone,
    _rehash_context,
    _sample_context,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.json"
SCHEMA = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.schema.json"
PLAN = ROOT / "docs/davida-provider-free-practice-administration-default-location-dry-run-plan.md"
DESIGN = ROOT / "docs/davida-provider-free-practice-administration-default-location-dry-run-design.md"
THREAT = ROOT / "docs/security/davida-provider-free-practice-administration-default-location-dry-run-threat-model-delta.md"
SCHEMA_SOURCE = ROOT / "app/schemas/practice_administration_default_location_proposal.py"
SERVICE_SOURCE = ROOT / "app/services/practice/practice_administration_default_location_dry_run.py"
ACCEPTANCE = ROOT / "scripts/davida_provider_free_practice_administration_default_location_dry_run_acceptance.py"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _result(candidate: object, context: object) -> dict:
    result = dry_run_default_location_proposal(
        candidate=candidate,  # type: ignore[arg-type]
        context_frame=context,  # type: ignore[arg-type]
    )
    DefaultLocationProposalResultAdapter.validate_python(result)
    return result


def _leaf_paths(value: object, prefix: tuple[object, ...] = ()) -> list[tuple[tuple[object, ...], object]]:
    leaves: list[tuple[tuple[object, ...], object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            leaves.extend(_leaf_paths(child, prefix + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            leaves.extend(_leaf_paths(child, prefix + (index,)))
    else:
        leaves.append((prefix, value))
    return leaves


def _mutated(value: object) -> object:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if value is None:
        return "tampered"
    return f"{value}__tampered"


def _set_path(value: object, path: tuple[object, ...], replacement: object) -> None:
    current = value
    for key in path[:-1]:
        current = current[key]  # type: ignore[index]
    current[path[-1]] = replacement  # type: ignore[index]


def test_contract_schema_is_recursively_closed_and_every_leaf_exact() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    contract = _json(CONTRACT)
    schema = _json(SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(contract)
    open_objects: list[str] = []

    def walk(value: object, path: str = "$") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                open_objects.append(path)
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(schema)
    assert not open_objects
    for path, original in _leaf_paths(contract):
        changed = copy.deepcopy(contract)
        _set_path(changed, path, _mutated(original))
        assert list(validator.iter_errors(changed)), path


def test_exact_change_and_current_null_change_release() -> None:
    context = _sample_context()
    result = _result(_candidate(context), context)
    assert result["verdict"] == "released"
    proposal = result["proposal_candidate"]
    assert proposal["artifact_type"] == "proposal_candidate"
    assert proposal["status"] == "dry_run_only"
    assert proposal["before_state"] == {
        "practitioner_ref": "prac_synth_0001",
        "default_location_ref": "loc_synth_0001",
    }
    assert proposal["after_state"] == {
        "practitioner_ref": "prac_synth_0001",
        "default_location_ref": "loc_synth_0002",
    }
    assert proposal["changed_paths"] == ["practitioner.default_location_ref"]
    assert proposal["authority_ceiling"] == PROPOSAL_AUTHORITY_CEILING
    assert proposal["human_confirmation_required"] is True

    null_context = _sample_context(current_null=True)
    null_result = _result(_candidate(null_context), null_context)
    assert null_result["proposal_candidate"]["before_state"]["default_location_ref"] is None


def test_repeat_output_and_hashes_are_deterministic_and_bound() -> None:
    context = _sample_context()
    candidate = _candidate(context)
    one = _result(candidate, context)
    two = _result(_json_clone(candidate), _json_clone(context))
    assert _canonical(one) == _canonical(two)
    proposal = one["proposal_candidate"]
    proposal_material = {
        "canonical_candidate": candidate,
        "context_revision": context["content_revision"],
        "source_paths": proposal["source_paths"],
        "before_state": proposal["before_state"],
        "after_state": proposal["after_state"],
    }
    expected = hashlib.sha256(_canonical(proposal_material).encode()).hexdigest()
    assert proposal["proposal_hash"] == expected
    grounding_material = {
        "canonical_candidate": candidate,
        "context_revision": context["content_revision"],
        "source_paths": sorted(proposal["source_paths"]),
        "before_state": proposal["before_state"],
        "after_state": proposal["after_state"],
    }
    expected_grounding = hashlib.sha256(
        _canonical(grounding_material).encode()
    ).hexdigest()
    assert proposal["grounding_hash"] == expected_grounding


def test_same_location_and_reference_errors_fail_closed() -> None:
    context = _sample_context()
    cases = (
        ({"location_ref": "loc_synth_0001"}, "no_change"),
        ({"practitioner_ref": "prac_synth_9999"}, "practitioner_not_resolved"),
        ({"location_ref": "loc_synth_9999"}, "location_not_resolved"),
        ({"practitioner_ref": "loc_synth_0001"}, "wrong_resource_kind"),
        ({"location_ref": "prac_synth_0002"}, "wrong_resource_kind"),
    )
    for update, reason in cases:
        result = _result(_candidate(context, **update), context)
        assert result["verdict"] == "rejected"
        assert result["reason"] == reason
        assert "proposal_candidate" not in result
        assert result["repair_performed"] is False
        assert result["retry_authorized"] is False


def test_duplicate_dangling_scope_and_revision_tampering_fail_closed() -> None:
    context = _sample_context()
    duplicate = _json_clone(context)
    duplicate["frames"]["practitioners"]["rows"].append(
        copy.deepcopy(duplicate["frames"]["practitioners"]["rows"][0])
    )
    duplicate["frames"]["practitioners"]["count"] = 3
    _rehash_context(duplicate)
    assert _result(_candidate(duplicate), duplicate)["reason"] == "context_boundary_invalid"

    dangling = _json_clone(context)
    dangling["frames"]["practitioners"]["rows"][0]["default_location_ref"] = "loc_synth_9999"
    _rehash_context(dangling)
    assert _result(_candidate(dangling), dangling)["reason"] == "context_boundary_invalid"

    for field, value in (
        ("practice_ref", "foreign_practice"),
        ("principal_ref", "foreign_principal"),
        ("correlation_id", "correlation-foreign"),
        ("content_revision", "f" * 64),
    ):
        assert _result(_candidate(context, **{field: value}), context)["reason"] == "scope_mismatch"

    stale_revision = _json_clone(context)
    stale_revision["frames"]["locations"]["rows"][0]["name"] = "Tampered"
    assert _result(_candidate(context), stale_revision)["reason"] == "context_revision_mismatch"


def test_unknown_effectful_and_other_operations_fail_before_release() -> None:
    assert ALLOWED_OPERATIONS == {OPERATION}
    assert REJECTION_REASONS == (
        "operation_not_allowed",
        "candidate_noncanonical",
        "candidate_schema_invalid",
        "input_over_bounded",
        "context_frame_invalid",
        "context_revision_mismatch",
        "context_boundary_invalid",
        "scope_mismatch",
        "evaluated_at_naive",
        "evaluated_at_out_of_range",
        "practitioner_not_resolved",
        "location_not_resolved",
        "wrong_resource_kind",
        "no_change",
    )
    assert {
        "authority_ceiling_invalid",
        "duplicate_resource_ref",
        "dangling_default_location",
    }.isdisjoint(REJECTION_REASONS)
    context = _sample_context()
    for operation in (
        "ADVISORY_EXPLAIN_DIRECTORY",
        "ADVISORY_SUMMARIZE_DIRECTORY",
        "PROPOSE_UPDATE_PRACTITIONER_PROFILE",
        "CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "APPLY_PRACTITIONER_UPDATE_DEFAULT_LOCATION",
        "WRITE_PRACTITIONER_DEFAULT_LOCATION",
        "UNKNOWN",
    ):
        result = _result(_candidate(context, operation=operation), context)
        assert result["reason"] == "operation_not_allowed"
        assert "proposal_candidate" not in result


def test_unknown_fields_authority_reversal_and_coercion_fail_closed() -> None:
    context = _sample_context()
    for field, value in (
        ("free_text", "forbidden"),
        ("before_state", {}),
        ("after_state", {}),
        ("command_payload", {}),
        ("idempotency_key", "forbidden"),
        ("confirmation_evidence", {}),
        ("audit_event", {}),
    ):
        result = _result(_candidate(context, **{field: value}), context)
        assert result["reason"] == "candidate_schema_invalid"
    for field in (
        "confirmation_authorized",
        "apply_authorized",
        "writes_authorized",
        "command_authorized",
        "provider_executed",
        "model_executed",
        "database_used",
        "network_used",
        "model_to_database",
    ):
        assert _result(_candidate(context, **{field: True}), context)["reason"] == "candidate_schema_invalid"
        assert _result(_candidate(context, **{field: 0}), context)["reason"] == "candidate_noncanonical"


def test_candidate_is_frozen_and_freshness_is_half_open() -> None:
    context = _sample_context()
    parsed = DefaultLocationProposalCandidate.model_validate(_candidate(context))
    with pytest.raises(Exception):
        parsed.location_ref = "loc_synth_0001"
    for evaluated_at, reason in (
        ("2026-08-03T14:01:00", "evaluated_at_naive"),
        ("2026-08-03T13:59:59Z", "evaluated_at_out_of_range"),
        ("2026-08-03T14:02:00Z", "evaluated_at_out_of_range"),
    ):
        assert _result(_candidate(context, evaluated_at=evaluated_at), context)["reason"] == reason


def test_source_has_no_effectful_import_or_clock_call() -> None:
    forbidden_imports = {
        "sqlalchemy",
        "requests",
        "httpx",
        "socket",
        "urllib",
        "time",
        "psycopg",
        "openai",
        "google",
        "fastapi",
        "starlette",
        "strawberry",
    }
    for path in (SCHEMA_SOURCE, SERVICE_SOURCE):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    calls.add(f"{node.func.value.id}.{node.func.attr}")
        assert not imports & forbidden_imports
        assert not {"datetime.now", "datetime.utcnow", "time.time"} & calls


def test_acceptance_script_passes_with_sanitized_lf_evidence(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    completed = subprocess.run(
        [sys.executable, str(ACCEPTANCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    evidence = json.loads(completed.stdout)
    assert evidence == _json(output)
    assert evidence["result"] == "provider_free_practice_administration_default_location_dry_run_pass"
    assert evidence["evidence_label"] == "provider_free_unoccupied_default_location_dry_run"
    assert evidence["failed_case_count"] == 0
    assert evidence["case_count"] == evidence["passed_case_count"]
    assert b"\r\n" not in output.read_bytes()
    serialized = output.read_text(encoding="utf-8")
    for forbidden in ("Avery", "Morgan", "prac_synth", "loc_synth", "practice_synth"):
        assert forbidden not in serialized


def test_docs_preserve_api_spine_and_closed_gates() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT))
    normalized = " ".join(text.split())
    assert "GraphQL remains read-only" in normalized
    assert "REST commands" in normalized
    assert "provider_free_unoccupied_default_location_dry_run" in text
    assert "no model/provider call" in text.lower()
    for gate in (
        "memory/RAG",
        "real identity/data",
        "patient/clinical/document",
        "confirmation",
        "apply/write",
        "deployment",
        "production",
        "release",
    ):
        assert gate in normalized
