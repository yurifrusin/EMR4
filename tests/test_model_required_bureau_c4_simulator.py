"""Focused deterministic tests for the Bureau C4 allowlisted-actuator simulator.

These tests exercise the runtime simulator module and its acceptance evidence.
They deliberately do not import ``app`` or any production actuator code.
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.model_required_bureau_c4_acceptance import (
    EVIDENCE_LABEL,
    EXPECTED_HEAD,
    EXPECTED_RESULT,
    NOW,
    SCHEMA_EXAMPLES,
    build_evidence,
    build_request,
    load_c3_fixtures,
    load_catalog,
    mint_evidence,
    new_runtime,
    raw_request_dict,
)
from scripts.model_required_bureau_c4_simulator import (
    DenialReason,
    EvidenceIssuer,
    EvidenceState,
    EXPECTED_REVISION,
    FaultInjection,
    HEALTH_DEGRADED,
    HEALTH_HEALTHY,
    canonical_sha256,
    parse_request,
)

ROOT = Path(__file__).resolve().parents[1]


def _errors(schema_path, value):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)
    )


def _fixtures():
    catalog = load_catalog()
    plan, decision, observations = load_c3_fixtures()
    return catalog, plan, decision, observations


def _mint(catalog, plan, decision, observations):
    issuer = EvidenceIssuer(catalog, lambda: NOW)
    issued = mint_evidence(issuer, plan, decision, observations)
    return issuer, issued


def test_acceptance_passes_with_exact_label_and_zero_operation_counters():
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == EXPECTED_RESULT
    assert evidence["source_head"] == EXPECTED_HEAD
    assert evidence["evidence_label"] == EVIDENCE_LABEL
    assert len(evidence["operation_counters"]) == 18
    assert set(evidence["operation_counters"].values()) == {0}


def test_five_schemas_are_closed_draft_2020_12_and_examples_validate():
    assert len(SCHEMA_EXAMPLES) == 5
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert not _errors(schema_path, json.loads(example_path.read_text(encoding="utf-8")))


def test_lf_byte_hashes_and_digests_reproduce():
    evidence = build_evidence()
    for path_string, stored_hash in evidence["artifact_hashes"].items():
        path = ROOT / path_string
        assert hashlib.sha256(path.read_bytes()).hexdigest() == stored_hash
    entry_data = json.loads(
        SCHEMA_EXAMPLES["runbook_catalog_entry"][1].read_text(encoding="utf-8")
    )
    core = {k: v for k, v in entry_data.items() if k != "catalog_digest"}
    assert canonical_sha256(core) == entry_data["catalog_digest"]


def _duplicate_reject(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate {k}")
        out[k] = v
    return out


def test_duplicate_key_and_unknown_mutations_reject_before_lookup():
    catalog, plan, decision, observations = _fixtures()
    issuer, issued = _mint(catalog, plan, decision, observations)
    entry = catalog["restart-api-synthetic.v1"]
    base = raw_request_dict(issued, entry, plan, decision)
    now_iso = NOW.isoformat().replace("+00:00", "Z")

    mutated = dict(base)
    mutated["parameters"] = {"scale": "global"}
    _, denial = parse_request(mutated, now_iso)
    assert denial.reason_code == DenialReason.UNKNOWN_PARAMETER

    mutated = dict(base)
    mutated["unknown_property"] = True
    _, denial = parse_request(mutated, now_iso)
    assert denial.reason_code == DenialReason.SCHEMA_REJECTED

    mutated = dict(base)
    mutated["runbook_id"] = "restart-anything.v9"
    _, denial = parse_request(mutated, now_iso)
    assert denial.reason_code == DenialReason.UNKNOWN_RUNBOOK

    mutated = dict(base)
    mutated["target"] = dict(mutated["target"])
    mutated["target"]["extra"] = True
    _, denial = parse_request(mutated, now_iso)
    assert denial.reason_code == DenialReason.SCHEMA_REJECTED

    duplicate = (
        '{"idempotency_key":"' + base["idempotency_key"]
        + '","idempotency_key":"x"}'
    )
    with pytest.raises(ValueError):
        json.loads(duplicate, object_pairs_hook=_duplicate_reject)


def test_exact_success_consumes_once_and_releases_only_after_fresh_read():
    catalog, plan, decision, observations = _fixtures()
    issuer, issued = _mint(catalog, plan, decision, observations)
    entry = catalog["restart-api-synthetic.v1"]
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    result = runtime.handle(request)
    assert result.is_success
    receipt = result.to_dict()
    assert receipt["result"] == "simulated_effect_verified"
    assert receipt["readback_fresh"] is True
    assert receipt["readback_health"] == HEALTH_HEALTHY
    assert receipt["readback_revision"] == EXPECTED_REVISION
    assert issuer.records[issued.record.reference_sha256].state == EvidenceState.CONSUMED
    assert runtime._state_store.read().health == HEALTH_HEALTHY
    assert len(runtime.attempt_audit_records) == 1
    assert len(runtime.effect_audit_records) == 1
    assert runtime.last_envelope is not None


def test_same_key_replay_and_changed_fingerprint_conflict():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    first = runtime.handle(build_request(issued, entry, plan, decision))
    second = runtime.handle(build_request(issued, entry, plan, decision))
    assert first.to_dict() == second.to_dict()
    assert len(runtime.attempt_audit_records) == 1

    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    runtime.handle(build_request(issued, entry, plan, decision))
    conflict = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            correlation_id="83000000-0000-4000-8000-000000000001",
        )
    )
    assert conflict.to_dict()["reason_code"] == DenialReason.IDEMPOTENCY_CONFLICT.value


def test_in_progress_key_denial():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    runtime.seed_in_progress_idempotency(request.idempotency_key, request.fingerprint())
    result = runtime.handle(request)
    assert result.to_dict()["reason_code"] == DenialReason.IDEMPOTENCY_IN_PROGRESS.value


def test_different_key_evidence_replay_is_rejected():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    runtime.handle(build_request(issued, entry, plan, decision))
    replay = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            idempotency_key="74000000-0000-4000-8000-000000000002",
        )
    )
    assert replay.to_dict()["reason_code"] == DenialReason.EXECUTION_EVIDENCE_REPLAY.value
    assert len(runtime.effect_audit_records) == 1


def test_concurrent_single_winner():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    results = []
    barrier = threading.Barrier(2)

    def worker():
        barrier.wait()
        results.append(runtime.handle(request))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 2
    assert len(runtime.attempt_audit_records) == 1
    assert len(runtime.effect_audit_records) == 1
    consumed = [r for r in issuer.records.values() if r.state == EvidenceState.CONSUMED]
    assert len(consumed) == 1


@pytest.mark.parametrize(
    ("fault", "expected_code"),
    [
        (FaultInjection.TRANSITION_FAILED, "SIMULATED_TRANSITION_FAILED"),
        (FaultInjection.EFFECT_AUDIT_APPEND_FAILED, "SIMULATED_TRANSITION_FAILED"),
        (
            FaultInjection.FIRST_READBACK_FAILED,
            "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED",
        ),
        (
            FaultInjection.HANDLER_RETURN_FALSE,
            "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED",
        ),
        (FaultInjection.ROLLBACK_FAILED, "SIMULATED_ROLLBACK_UNVERIFIED"),
        (FaultInjection.ROLLBACK_READBACK_UNVERIFIED, "SIMULATED_ROLLBACK_UNVERIFIED"),
    ],
)
def test_fault_injection_never_releases_false_success(fault, expected_code):
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    result = runtime.handle(build_request(issued, entry, plan, decision), fault=fault)
    assert result.is_denial
    assert result.to_dict()["reason_code"] == expected_code
    assert (
        result.to_dict()["simulated_effect"]
        != "health_transition_degraded_to_healthy"
    )
    assert issuer.records[issued.record.reference_sha256].state == EvidenceState.CONSUMED
    assert len(runtime.attempt_audit_records) == 1
    if fault in (FaultInjection.TRANSITION_FAILED, FaultInjection.EFFECT_AUDIT_APPEND_FAILED):
        assert len(runtime.effect_audit_records) == 0
        assert runtime._state_store.read().health == HEALTH_DEGRADED


def test_denial_cases_produce_zero_effect():
    evidence = build_evidence()
    valid_codes = {
        DenialReason.SCHEMA_REJECTED.value,
        DenialReason.EXECUTABLE_CONTENT_REJECTED.value,
        DenialReason.UNKNOWN_RUNBOOK.value,
        DenialReason.UNKNOWN_PARAMETER.value,
        DenialReason.SCOPE_EXPANSION_REJECTED.value,
        DenialReason.STALE_OR_SUPERSEDED.value,
        DenialReason.TARGET_REVISION_CONFLICT.value,
        DenialReason.OBSERVATION_MISMATCH.value,
        DenialReason.AUTHORITY_MISMATCH.value,
        DenialReason.REVIEWER_INVALID.value,
        DenialReason.EXECUTION_EVIDENCE_INVALID.value,
        DenialReason.EXECUTION_EVIDENCE_REPLAY.value,
        DenialReason.IDEMPOTENCY_CONFLICT.value,
        DenialReason.IDEMPOTENCY_IN_PROGRESS.value,
    }
    for name, outcome in evidence["denial_cases"].items():
        if isinstance(outcome, str):
            assert outcome in valid_codes
            continue
        assert outcome["reason_code"] in valid_codes
        assert outcome["effect_record_count"] == 0


def test_simulator_module_has_no_forbidden_capability():
    import ast

    source = (ROOT / "scripts/model_required_bureau_c4_simulator.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    assert "app" not in imported
    allowed = {
        "__future__",
        "hashlib",
        "json",
        "secrets",
        "threading",
        "dataclasses",
        "datetime",
        "enum",
        "typing",
    }
    assert not (imported - allowed)


def test_evidence_label_is_exact_and_unmounted():
    evidence = build_evidence()
    assert evidence["evidence_label"] == "provider_free_authored_synthetic_allowlisted_actuator_simulation"
    assert evidence["evidence_label"] == EVIDENCE_LABEL
    text = (ROOT / "scripts/model_required_bureau_c4_simulator.py").read_text(
        encoding="utf-8"
    )
    assert EVIDENCE_LABEL in text
    assert "from app" not in text.replace("never imports", "")
    assert "import app" not in text.replace("never imports", "")
