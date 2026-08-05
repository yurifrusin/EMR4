"""Focused deterministic tests for the Bureau C4 allowlisted-actuator simulator.

These tests exercise the runtime simulator module and its acceptance evidence.
They deliberately do not import ``app`` or any production actuator code.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import threading
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

import scripts.model_required_bureau_c4_simulator as c4

from scripts.model_required_bureau_c4_acceptance import (
    ACTOR_ID,
    CORRELATION_ID,
    EVIDENCE_LABEL,
    EXPECTED_HEAD,
    EXPECTED_RESULT,
    GENERATOR_ID,
    NOW,
    NOW_ISO,
    REQUIRED_ROLE,
    REVIEWER_ID,
    SCHEMA_EXAMPLES,
    _authority_store,
    build_evidence,
    build_request,
    load_c3_fixtures,
    load_catalog,
    mint_evidence,
    new_runtime,
    raw_request_dict,
)
from scripts.model_required_bureau_c4_simulator import (
    Actor,
    CurrentObservation,
    DenialReason,
    EvidenceIssuer,
    EvidenceState,
    EXPECTED_REVISION,
    FaultInjection,
    HEALTH_DEGRADED,
    HEALTH_HEALTHY,
    InMemoryAuditLog,
    InMemoryStateStore,
    IssuanceDenied,
    PLAN_ENVIRONMENT,
    RunbookId,
    SyntheticServiceState,
    TARGET_ID,
    TARGET_KIND,
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


def test_two_runtime_instances_share_one_evidence_transaction_and_attempt_sequence():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    authority = _authority_store(entry, plan, decision, observations)
    state_store = InMemoryStateStore()
    attempt_audit = InMemoryAuditLog()
    effect_audit = InMemoryAuditLog()
    runtimes = [
        new_runtime(
            catalog,
            issuer,
            authority_store=authority,
            state_store=state_store,
            attempt_audit=attempt_audit,
            effect_audit=effect_audit,
        )
        for _ in range(2)
    ]
    requests = [
        build_request(issued, entry, plan, decision),
        build_request(
            issued,
            entry,
            plan,
            decision,
            idempotency_key="74000000-0000-4000-8000-000000000002",
        ),
    ]
    barrier = threading.Barrier(2)
    results = []

    def worker(index):
        barrier.wait()
        results.append(runtimes[index].handle(requests[index]))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    codes = sorted(result.to_dict().get("reason_code", "SUCCESS") for result in results)
    assert codes == [DenialReason.EXECUTION_EVIDENCE_REPLAY.value, "SUCCESS"]
    assert len(attempt_audit.read()) == 1
    assert len(effect_audit.read()) == 1
    assert attempt_audit.read()[0]["attempt_id"] == "c4-attempt-000000000001"
    assert issuer.records[issued.record.reference_sha256].state == EvidenceState.CONSUMED


def test_two_runtime_instances_share_same_key_terminal_replay():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    authority = _authority_store(entry, plan, decision, observations)
    state_store = InMemoryStateStore()
    attempt_audit = InMemoryAuditLog()
    effect_audit = InMemoryAuditLog()
    runtimes = [
        new_runtime(
            catalog,
            issuer,
            authority_store=authority,
            state_store=state_store,
            attempt_audit=attempt_audit,
            effect_audit=effect_audit,
        )
        for _ in range(2)
    ]
    request = build_request(issued, entry, plan, decision)
    first = runtimes[0].handle(request)
    replay = runtimes[1].handle(request)
    assert first.to_dict() == replay.to_dict()
    assert len(attempt_audit.read()) == 1
    assert len(effect_audit.read()) == 1


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
    # Effect audit is retained only for verified success: every denial/rollback
    # failure path restores the effect-audit snapshot.
    assert len(runtime.effect_audit_records) == 0
    if fault in (FaultInjection.TRANSITION_FAILED, FaultInjection.EFFECT_AUDIT_APPEND_FAILED):
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
        "re",
        "secrets",
        "threading",
        "contextlib",
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


# --------------------------------------------------------------------------- #
# Findings regression tests
# --------------------------------------------------------------------------- #

def _zero_change_snapshot(runtime, issuer):
    return {
        "state": runtime._state_store.read().to_dict(),
        "evidence": {k: v.to_dict() for k, v in issuer.records.items()},
        "idempotency": dict(runtime.idempotency_records),
        "attempt": list(runtime.attempt_audit_records),
        "effect": list(runtime.effect_audit_records),
    }


def test_scalar_admission_rejects_numeric_idempotency_key_with_zero_change():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    base = raw_request_dict(issued, entry, plan, decision)
    before = _zero_change_snapshot(runtime, issuer)

    mutated = copy.deepcopy(base)
    mutated["idempotency_key"] = 74000000  # numeric idempotency key (reproduced)
    request, denial = parse_request(mutated, NOW_ISO)
    assert request is None
    assert denial is not None
    assert denial.reason_code == DenialReason.SCHEMA_REJECTED
    assert _zero_change_snapshot(runtime, issuer) == before


def test_scalar_admission_rejects_all_field_type_mutations():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    base = raw_request_dict(issued, entry, plan, decision)
    before = _zero_change_snapshot(runtime, issuer)

    mutations = {
        "idempotency_key": True,
        "correlation_id": 42,
        "actor.actor_id": None,
        "actor.role": 9,
        "evidence_reference": "",
        "runbook_id": 7,
        "target.environment": False,
        "target.kind": 3,
        "target.target_id": None,
        "target.expected_revision": 5,
        "parameters": [],
        "plan_binding.plan_id": True,
        "plan_binding.plan_revision": True,  # boolean must not satisfy integer
        "plan_binding.plan_sha256": 123,
        "decision_binding.decision_id": 1,
        "decision_binding.decision_sha256": False,
        "decision_binding.policy_version": 0,
        "catalog_binding.catalog_version": False,
        "catalog_binding.catalog_digest": 0,
        "supersession_key": 99,
        "readback_contract.health": None,
        "readback_contract.revision": False,
    }

    def apply_mutation(mutated, path, value):
        parts = path.split(".")
        target = mutated
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = value

    for path, value in mutations.items():
        mutated = copy.deepcopy(base)
        apply_mutation(mutated, path, value)
        request, denial = parse_request(mutated, NOW_ISO)
        assert request is None, f"admitted invalid mutation: {path}"
        assert denial is not None, f"no denial for: {path}"
        assert _zero_change_snapshot(runtime, issuer) == before


def test_readback_compares_full_actual_target_tuple():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    wrong_states = [
        SyntheticServiceState(PLAN_ENVIRONMENT, TARGET_KIND, "synthetic:wrong-service", EXPECTED_REVISION, HEALTH_DEGRADED),
        SyntheticServiceState("staging", TARGET_KIND, TARGET_ID, EXPECTED_REVISION, HEALTH_DEGRADED),
        SyntheticServiceState(PLAN_ENVIRONMENT, "database", TARGET_ID, EXPECTED_REVISION, HEALTH_DEGRADED),
        SyntheticServiceState(PLAN_ENVIRONMENT, TARGET_KIND, TARGET_ID, "9.9.9", HEALTH_DEGRADED),
    ]
    for seeded in wrong_states:
        issuer, issued = _mint(catalog, plan, decision, observations)
        runtime = new_runtime(catalog, issuer)
        runtime._state_store.write(seeded)
        result = runtime.handle(build_request(issued, entry, plan, decision))
        assert result.is_denial, f"false success for seeded target {seeded.to_dict()}"
        assert len(runtime.effect_audit_records) == 0

    # Success receipt target derives from the verified fresh readback.
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    result = runtime.handle(build_request(issued, entry, plan, decision))
    assert result.is_success
    receipt = result.to_dict()
    assert receipt["target"] == entry.target.to_dict()


def test_current_authority_denials_fail_closed():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]

    def run_with_mutator(mutator):
        issuer, issued = _mint(catalog, plan, decision, observations)
        store = _authority_store(entry, plan, decision, observations)
        mutator(store)
        runtime = new_runtime(catalog, issuer, authority_store=store)
        result = runtime.handle(build_request(issued, entry, plan, decision))
        return result, runtime

    def set_snap(store):
        snap = store.snapshot()
        store.set_snapshot(snap)

    cases = {
        "catalog_replacement": (
            lambda s: s.set_snapshot(replace(s.snapshot(), catalog_digest="0" * 64)),
            DenialReason.AUTHORITY_MISMATCH,
        ),
        "plan_drift": (
            lambda s: s.set_snapshot(replace(s.snapshot(), plan_sha256="1" * 64)),
            DenialReason.AUTHORITY_MISMATCH,
        ),
        "plan_supersession": (
            lambda s: s.set_snapshot(replace(s.snapshot(), plan_superseded=True)),
            DenialReason.STALE_OR_SUPERSEDED,
        ),
        "decision_supersession": (
            lambda s: s.set_snapshot(replace(s.snapshot(), decision_superseded=True)),
            DenialReason.STALE_OR_SUPERSEDED,
        ),
        "actor_role_loss": (
            lambda s: s.set_snapshot(replace(s.snapshot(), actor_role="practice_manager")),
            DenialReason.AUTHORITY_MISMATCH,
        ),
        "actor_expiry": (
            lambda s: s.set_snapshot(replace(s.snapshot(), actor_expires_at="2026-08-04T08:00:00Z")),
            DenialReason.STALE_OR_SUPERSEDED,
        ),
        "reviewer_expiry": (
            lambda s: s.set_snapshot(replace(s.snapshot(), reviewer_expires_at="2026-08-04T08:00:00Z")),
            DenialReason.STALE_OR_SUPERSEDED,
        ),
        "reviewer_role_loss": (
            lambda s: s.set_snapshot(
                replace(s.snapshot(), reviewer_role="revoked_but_nonempty")
            ),
            DenialReason.REVIEWER_INVALID,
        ),
        "reviewer_separation_loss": (
            lambda s: s.set_snapshot(replace(s.snapshot(), reviewer_id=s.snapshot().generator_id)),
            DenialReason.REVIEWER_INVALID,
        ),
        "observation_content_drift": (
            lambda s: s.set_snapshot(
                replace(
                    s.snapshot(),
                    observations=tuple(
                        CurrentObservation(o.observation_id, "0" * 64, o.observed_at, o.expires_at, o.must_be_fresh)
                        if o.observation_id == "api-health"
                        else o
                        for o in s.snapshot().observations
                    ),
                )
            ),
            DenialReason.OBSERVATION_MISMATCH,
        ),
        "missing_current_records": (
            lambda s: s.set_snapshot(None),
            DenialReason.STALE_OR_SUPERSEDED,
        ),
    }
    for name, (mutator, expected) in cases.items():
        result, runtime = run_with_mutator(mutator)
        assert result.is_denial, f"{name}: false success"
        assert result.to_dict()["reason_code"] == expected.value, name
        assert len(runtime.effect_audit_records) == 0, name


def test_current_authority_mutation_cannot_interleave_between_validation_and_effect():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]
    issuer, issued = _mint(catalog, plan, decision, observations)
    authority = _authority_store(entry, plan, decision, observations)
    runtime = new_runtime(catalog, issuer, authority_store=authority)
    request = build_request(issued, entry, plan, decision)
    revoked = replace(authority.snapshot(), actor_role="revoked_but_nonempty")
    entered_transition = threading.Event()
    release_transition = threading.Event()
    mutation_started = threading.Event()
    mutation_finished = threading.Event()
    results = []
    runbook = RunbookId.RESTART_API_SYNTHETIC_V1
    original_transition = c4._RUNBOOK_CALLABLES[runbook]

    def blocking_transition(state):
        entered_transition.set()
        assert release_transition.wait(timeout=2)
        return original_transition(state)

    def revoke_authority():
        mutation_started.set()
        authority.set_snapshot(revoked)
        mutation_finished.set()

    handler_thread = threading.Thread(target=lambda: results.append(runtime.handle(request)))
    mutation_thread = threading.Thread(target=revoke_authority)
    c4._RUNBOOK_CALLABLES[runbook] = blocking_transition
    try:
        handler_thread.start()
        assert entered_transition.wait(timeout=2)
        mutation_thread.start()
        assert mutation_started.wait(timeout=2)
        assert not mutation_finished.wait(timeout=0.05)
        release_transition.set()
        handler_thread.join(timeout=2)
        mutation_thread.join(timeout=2)
    finally:
        release_transition.set()
        c4._RUNBOOK_CALLABLES[runbook] = original_transition
        handler_thread.join(timeout=2)
        if mutation_thread.ident is not None:
            mutation_thread.join(timeout=2)

    assert not handler_thread.is_alive()
    assert not mutation_thread.is_alive()
    assert mutation_finished.is_set()
    assert len(results) == 1 and results[0].is_success

    followup_issuer, followup_issued = _mint(catalog, plan, decision, observations)
    followup_runtime = new_runtime(
        catalog, followup_issuer, authority_store=authority
    )
    followup = followup_runtime.handle(
        build_request(followup_issued, entry, plan, decision)
    )
    assert followup.to_dict()["reason_code"] == DenialReason.AUTHORITY_MISMATCH.value
    assert len(followup_runtime.effect_audit_records) == 0


def test_effect_audit_retained_only_for_verified_success():
    catalog, plan, decision, observations = _fixtures()
    entry = catalog["restart-api-synthetic.v1"]

    for fault in FaultInjection:
        if fault == FaultInjection.NONE:
            continue
        issuer, issued = _mint(catalog, plan, decision, observations)
        runtime = new_runtime(catalog, issuer)
        result = runtime.handle(build_request(issued, entry, plan, decision), fault=fault)
        assert result.is_denial
        assert len(runtime.effect_audit_records) == 0, f"{fault.value}: effect audit retained"
        assert len(runtime.attempt_audit_records) == 1

    # Success has exactly one retained effect record.
    issuer, issued = _mint(catalog, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    result = runtime.handle(build_request(issued, entry, plan, decision))
    assert result.is_success
    assert len(runtime.effect_audit_records) == 1


def test_counter_schemas_enumerate_exact_18_names_and_reject_mutations():
    expected_names = [
        "filesystem_operations", "process_operations", "shell_operations", "sql_operations",
        "socket_operations", "network_operations", "database_operations", "container_operations",
        "cloud_operations", "iam_operations", "secret_store_operations", "product_route_operations",
        "provider_operations", "external_event_operations", "dynamic_import_operations",
        "eval_exec_operations", "reflection_operations", "template_url_path_operations",
    ]
    assert len(expected_names) == 18
    for label in ("execution", "denial"):
        schema_path = SCHEMA_EXAMPLES[f"simulator_{label}_receipt"][0]
        example_path = SCHEMA_EXAMPLES[f"simulator_{label}_receipt"][1]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        counters_schema = schema["properties"]["operation_counters"]
        assert counters_schema["additionalProperties"] is False
        assert set(counters_schema["required"]) == set(expected_names)
        assert set(counters_schema["properties"].keys()) == set(expected_names)
        assert all(counters_schema["properties"][name]["const"] == 0 for name in expected_names)

        base = json.loads(example_path.read_text(encoding="utf-8"))
        original = dict(base["operation_counters"])

        renamed = dict(base)
        renamed["operation_counters"] = {f"arbitrary_{i}": 0 for i in range(18)}
        assert _errors(schema_path, renamed), f"{label}: renamed counters admitted"

        for name in expected_names:
            omitted = dict(base)
            omitted["operation_counters"] = {k: v for k, v in original.items() if k != name}
            assert _errors(schema_path, omitted), f"{label}: omitted {name} admitted"

        extra = dict(base)
        extra["operation_counters"] = dict(original)
        extra["operation_counters"]["extra_operation"] = 0
        assert _errors(schema_path, extra), f"{label}: extra counter admitted"

        nonzero = dict(base)
        nonzero["operation_counters"] = dict(original)
        nonzero["operation_counters"]["filesystem_operations"] = 1
        assert _errors(schema_path, nonzero), f"{label}: non-zero counter admitted"


def test_production_mint_signature_has_no_reference_or_nonce():
    signature = inspect.signature(EvidenceIssuer.mint)
    assert "reference" not in signature.parameters
    assert "nonce" not in signature.parameters


def test_two_unpatched_issuances_produce_different_values_and_digests():
    catalog, plan, decision, observations = _fixtures()

    def mint_once():
        return EvidenceIssuer(catalog, lambda: NOW).mint(
            plan=plan,
            decision=decision,
            candidate_generator_id=GENERATOR_ID,
            reviewer_id=REVIEWER_ID,
            actor=Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
            observations=observations,
            correlation_id=CORRELATION_ID,
            actor_expires_at="2026-08-04T08:01:00Z",
            reviewer_expires_at="2026-08-04T08:01:00Z",
        )

    first = mint_once()
    second = mint_once()
    assert first.reference != second.reference
    assert first.record.nonce != second.record.nonce
    assert first.record.reference_sha256 != second.record.reference_sha256


def test_issuance_uniqueness_concurrency_barrier_single_winner():
    catalog, plan, decision, observations = _fixtures()
    contender_count = 8
    issuer = EvidenceIssuer(catalog, lambda: NOW)
    barrier = threading.Barrier(contender_count)
    results = []

    def worker():
        barrier.wait()
        try:
            issued = issuer.mint(
                plan=plan,
                decision=decision,
                candidate_generator_id=GENERATOR_ID,
                reviewer_id=REVIEWER_ID,
                actor=Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
                observations=observations,
                correlation_id=CORRELATION_ID,
                actor_expires_at="2026-08-04T08:01:00Z",
                reviewer_expires_at="2026-08-04T08:01:00Z",
            )
            results.append(("ok", issued.record.evidence_id))
        except IssuanceDenied as error:
            results.append((error.reason.value, None))

    threads = [threading.Thread(target=worker) for _ in range(contender_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sum(1 for r in results if r[0] == "ok") == 1
    assert sum(1 for r in results if r[0] == "STALE_OR_SUPERSEDED") == contender_count - 1
    assert len(issuer.records) == 1
    assert len(issuer._issued_keys) == 1


def test_evidence_includes_new_repair_sections():
    evidence = build_evidence()
    for section in (
        "scalar_admission",
        "target_readback",
        "current_authority",
        "counter_schemas",
        "production_entropy",
        "issuance_concurrency",
        "sol_recovery_guards",
    ):
        assert section in evidence, f"evidence missing section {section}"
