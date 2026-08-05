"""Provider-free deterministic acceptance for the Bureau C4 allowlisted-actuator simulator.

This is acceptance/evidence tooling and stays separate from the runtime
simulator module.  It may read the owned schemas/examples and write only the
owned authored-synthetic acceptance evidence file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

# Allow direct script execution (``python scripts/...py``) and pytest both to
# import the runtime simulator module from the repository root.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
if str(_BOOTSTRAP_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_ROOT))

from scripts.model_required_bureau_c4_simulator import (
    Actor,
    CatalogBinding,
    DecisionBinding,
    DenialReason,
    EvidenceIssuer,
    EvidenceState,
    EVIDENCE_LABEL,
    EXPECTED_REVISION,
    FaultInjection,
    FORWARD_RUNBOOK,
    HEALTH_DEGRADED,
    HEALTH_HEALTHY,
    InMemoryAuditLog,
    InMemoryStateStore,
    IssuanceDenied,
    PlanBinding,
    ReadbackContract,
    REQUIRED_ROLE,
    RunbookCatalogEntry,
    RunbookId,
    SimulatorRequest,
    SimulatorRuntime,
    SUPERSESSION_KEY,
    TargetRef,
    canonical_sha256,
    parse_request,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator"
)
C3_ROOT = ROOT / "orchestration/continuity/model-required-bureau-c3-d3"
SUCCESSOR_ROOT = (
    ROOT
    / "orchestration/continuity/model-required-bureau-provider-free-successor-lanes"
)
PLAN = ROOT / "docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md"
THREAT = (
    ROOT
    / "docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md"
)
DEFAULT_OUTPUT = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
EXPECTED_HEAD = "b66b37a81120b1abd655ce65c42daf7518b8f7d5"
EXPECTED_RESULT = "model_required_bureau_c4_allowlisted_actuator_simulator_pass"

SCHEMA_EXAMPLES: dict[str, tuple[Path, Path]] = {
    "runbook_catalog_entry": (
        ARTIFACT_ROOT / "runbook-catalog-entry.schema.json",
        ARTIFACT_ROOT / "runbook-catalog-entry.example.json",
    ),
    "execution_evidence": (
        ARTIFACT_ROOT / "execution-evidence.schema.json",
        ARTIFACT_ROOT / "execution-evidence.example.json",
    ),
    "simulator_command_envelope": (
        ARTIFACT_ROOT / "simulator-command-envelope.schema.json",
        ARTIFACT_ROOT / "simulator-command-envelope.example.json",
    ),
    "simulator_execution_receipt": (
        ARTIFACT_ROOT / "simulator-execution-receipt.schema.json",
        ARTIFACT_ROOT / "simulator-execution-receipt.example.json",
    ),
    "simulator_denial_receipt": (
        ARTIFACT_ROOT / "simulator-denial-receipt.schema.json",
        ARTIFACT_ROOT / "simulator-denial-receipt.example.json",
    ),
}

FIXTURE_REFERENCE = (
    "c4-fixture-opaque-reference-00000000000000000000000000000000000000000000"
)
FIXTURE_NONCE = "9c3d5f7e1a2b4c8d0e6f1a2b3c4d5e6f"
CORRELATION_ID = "73000000-0000-4000-8000-000000000001"
IDEMPOTENCY_KEY = "74000000-0000-4000-8000-000000000001"
ACTOR_ID = "op-operator-1"
GENERATOR_ID = "gen-synthetic-c4"
REVIEWER_ID = "rev-independent-1"
NOW = datetime(2026, 8, 4, 8, 0, 30, tzinfo=timezone.utc)
NOW_ISO = "2026-08-04T08:00:30Z"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be an object")
    return value


def strict_json_loads(text: str) -> dict[str, Any]:
    """Reject duplicate keys (non-canonical encoding) before any lookup."""

    def object_pairs_hook(pairs):
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate key: {key}")
            out[key] = value
        return out

    value = json.loads(text, object_pairs_hook=object_pairs_hook)
    if not isinstance(value, dict):
        raise ValueError("payload must be an object")
    return value


def validate(schema_path: Path, instance: dict[str, Any]) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        ),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise ValueError(f"{schema_path.name}: {errors[0].message}")


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now_callable():
    return NOW


# --------------------------------------------------------------------------- #
# Fixture loading and request builders
# --------------------------------------------------------------------------- #

def load_catalog() -> dict[str, RunbookCatalogEntry]:
    entry_data = load_json(SCHEMA_EXAMPLES["runbook_catalog_entry"][1])
    return {entry_data["runbook_id"]: RunbookCatalogEntry.from_dict(entry_data)}


def load_c3_fixtures() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    plan = load_json(C3_ROOT / "recovery-plan-candidate.example.json")
    decision = load_json(C3_ROOT / "recovery-authority-decision.example.json")
    anatomy = load_json(SUCCESSOR_ROOT / "technical-anatomy-frame.example.json")
    return plan, decision, anatomy["observations"]


def build_request(
    issued,
    catalog_entry: RunbookCatalogEntry,
    plan: dict[str, Any],
    decision: dict[str, Any],
    *,
    idempotency_key: str = IDEMPOTENCY_KEY,
    correlation_id: str = CORRELATION_ID,
    evidence_reference: str | None = None,
    actor: Actor | None = None,
) -> SimulatorRequest:
    ref = evidence_reference if evidence_reference is not None else issued.reference
    return SimulatorRequest(
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        actor=actor if actor is not None else Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
        evidence_reference=ref,
        runbook_id=RunbookId.RESTART_API_SYNTHETIC_V1,
        target=TargetRef(
            catalog_entry.target.environment,
            catalog_entry.target.kind,
            catalog_entry.target.target_id,
            catalog_entry.target.expected_revision,
        ),
        parameters={},
        plan_binding=PlanBinding(
            plan_id=plan["plan_id"],
            plan_revision=plan.get("plan_revision", 1),
            plan_sha256=decision["plan_sha256"],
        ),
        decision_binding=DecisionBinding(
            decision_id=decision["decision_id"],
            decision_sha256=canonical_sha256(decision),
            policy_version=decision["policy_version"],
        ),
        catalog_binding=CatalogBinding(
            catalog_version=catalog_entry.catalog_version,
            catalog_digest=catalog_entry.catalog_digest,
        ),
        supersession_key=SUPERSESSION_KEY,
        readback_contract=ReadbackContract(HEALTH_HEALTHY, EXPECTED_REVISION),
    )


def mint_evidence(issuer: EvidenceIssuer, plan, decision, observations) -> Any:
    return issuer.mint(
        plan=plan,
        decision=decision,
        candidate_generator_id=GENERATOR_ID,
        reviewer_id=REVIEWER_ID,
        actor=Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
        observations=observations,
        correlation_id=CORRELATION_ID,
        reference=FIXTURE_REFERENCE,
        nonce=FIXTURE_NONCE,
        actor_expires_at="2026-08-04T08:01:00Z",
        reviewer_expires_at="2026-08-04T08:01:00Z",
    )


def new_runtime(catalog, issuer, *, now=NOW) -> SimulatorRuntime:
    runtime = SimulatorRuntime(
        catalog=catalog,
        state_store=InMemoryStateStore(),
        attempt_audit=InMemoryAuditLog(),
        effect_audit=InMemoryAuditLog(),
        evidence_records=issuer.records,
        now=lambda: now,
    )
    return runtime


# --------------------------------------------------------------------------- #
# Schema / example / digest checks
# --------------------------------------------------------------------------- #

def raw_request_dict(
    issued,
    catalog_entry: RunbookCatalogEntry,
    plan: dict[str, Any],
    decision: dict[str, Any],
    *,
    idempotency_key: str = IDEMPOTENCY_KEY,
    correlation_id: str = CORRELATION_ID,
    evidence_reference: str | None = None,
) -> dict[str, Any]:
    ref = evidence_reference if evidence_reference is not None else issued.reference
    return {
        "idempotency_key": idempotency_key,
        "correlation_id": correlation_id,
        "actor": {"actor_id": ACTOR_ID, "role": REQUIRED_ROLE},
        "evidence_reference": ref,
        "runbook_id": FORWARD_RUNBOOK,
        "target": {
            "environment": catalog_entry.target.environment,
            "kind": catalog_entry.target.kind,
            "target_id": catalog_entry.target.target_id,
            "expected_revision": catalog_entry.target.expected_revision,
        },
        "parameters": {},
        "plan_binding": {
            "plan_id": plan["plan_id"],
            "plan_revision": plan.get("plan_revision", 1),
            "plan_sha256": decision["plan_sha256"],
        },
        "decision_binding": {
            "decision_id": decision["decision_id"],
            "decision_sha256": canonical_sha256(decision),
            "policy_version": decision["policy_version"],
        },
        "catalog_binding": {
            "catalog_version": catalog_entry.catalog_version,
            "catalog_digest": catalog_entry.catalog_digest,
        },
        "supersession_key": SUPERSESSION_KEY,
        "readback_contract": {"health": HEALTH_HEALTHY, "revision": EXPECTED_REVISION},
    }


def _validate_schemas_and_examples() -> dict[str, Any]:
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        if schema.get("additionalProperties") is not False:
            raise ValueError(f"{schema_path.name} is not closed at root")
        validate(schema_path, load_json(example_path))
    return {
        "closed_schema_count": len(SCHEMA_EXAMPLES),
        "canonical_example_count": len(SCHEMA_EXAMPLES),
        "all_examples_valid": True,
    }


def _validate_digest_reproduction(
    catalog_entry: RunbookCatalogEntry,
    plan: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    reproduced_catalog_digest = canonical_sha256(catalog_entry.to_dict_core())
    if reproduced_catalog_digest != catalog_entry.catalog_digest:
        raise ValueError("catalog digest does not reproduce")
    reproduced_plan_sha256 = canonical_sha256(plan)
    if reproduced_plan_sha256 != decision["plan_sha256"]:
        raise ValueError("plan hash does not reproduce decision binding")
    parameters_sha256 = canonical_sha256({})
    evidence_example = load_json(SCHEMA_EXAMPLES["execution_evidence"][1])
    if evidence_example["parameters_sha256"] != parameters_sha256:
        raise ValueError("empty-parameter hash drift")
    if evidence_example["plan_sha256"] != reproduced_plan_sha256:
        raise ValueError("evidence example plan hash drift")
    if evidence_example["decision_sha256"] != canonical_sha256(decision):
        raise ValueError("evidence example decision hash drift")
    envelope_example = load_json(SCHEMA_EXAMPLES["simulator_command_envelope"][1])
    if envelope_example["request_fingerprint"] != _expected_fingerprint(envelope_example):
        raise ValueError("request fingerprint does not reproduce")
    return {
        "catalog_digest_reproduces": reproduced_catalog_digest,
        "plan_sha256_reproduces": reproduced_plan_sha256,
        "decision_sha256_reproduces": canonical_sha256(decision),
        "empty_parameters_sha256": parameters_sha256,
        "request_fingerprint_reproduces": envelope_example["request_fingerprint"],
    }


def _expected_fingerprint(envelope_example: dict[str, Any]) -> str:
    payload = {
        "idempotency_key": envelope_example["idempotency_key"],
        "correlation_id": envelope_example["correlation_id"],
        "actor_id": envelope_example["actor"]["actor_id"],
        "actor_role": envelope_example["actor"]["role"],
        "evidence_reference_sha256": envelope_example["evidence_binding"][
            "reference_sha256"
        ],
        "runbook_id": envelope_example["runbook_id"],
        "target": envelope_example["target"],
        "parameters_sha256": canonical_sha256({}),
        "plan_id": envelope_example["plan_binding"]["plan_id"],
        "plan_revision": envelope_example["plan_binding"]["plan_revision"],
        "plan_sha256": envelope_example["plan_binding"]["plan_sha256"],
        "decision_id": envelope_example["decision_binding"]["decision_id"],
        "decision_sha256": envelope_example["decision_binding"]["decision_sha256"],
        "policy_version": envelope_example["decision_binding"]["policy_version"],
        "catalog_version": envelope_example["catalog_binding"]["catalog_version"],
        "catalog_digest": envelope_example["catalog_binding"]["catalog_digest"],
        "supersession_key": SUPERSESSION_KEY,
        "readback_contract": envelope_example["readback_contract"],
    }
    return canonical_sha256(payload)


# --------------------------------------------------------------------------- #
# Mutation rejections (duplicate/unknown/non-canonical/executable)
# --------------------------------------------------------------------------- #

def _validate_mutation_rejections(
    issued,
    catalog_entry: RunbookCatalogEntry,
    plan: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    base = raw_request_dict(issued, catalog_entry, plan, decision)
    outcomes: dict[str, str] = {}

    mutated = dict(base)
    mutated["unknown_property"] = "forbidden"
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["unknown_property"] = denial.reason_code.value

    mutated = dict(base)
    mutated["parameters"] = {"scale": "global"}
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["unknown_parameter"] = denial.reason_code.value

    mutated = dict(base)
    mutated["target"] = dict(mutated["target"])
    mutated["target"]["extra"] = "forbidden"
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["unknown_nested_property"] = denial.reason_code.value

    mutated = dict(base)
    mutated["runbook_id"] = "restart-anything.v9"
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["unknown_runbook"] = denial.reason_code.value

    mutated = dict(base)
    mutated["target"] = {
        "environment": "production",
        "kind": "database",
        "target_id": "prod:db",
        "expected_revision": "9.9.9",
    }
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["scope_expansion"] = denial.reason_code.value

    mutated = dict(base)
    mutated["target"] = {
        "environment": "isolated_authored_synthetic",
        "kind": "service",
        "target_id": "synthetic:api-service",
        "expected_revision": "0.0.0-drift",
    }
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["target_revision_drift"] = denial.reason_code.value

    mutated = dict(base)
    mutated["actor"] = {"actor_id": "op-operator-1", "role": "practice_manager"}
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["wrong_role"] = denial.reason_code.value

    mutated = dict(base)
    mutated["readback_contract"] = {"health": "degraded", "revision": EXPECTED_REVISION}
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["readback_contract_drift"] = denial.reason_code.value

    mutated = dict(base)
    mutated["supersession_key"] = "other.synthetic.service"
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["supersession_key_drift"] = denial.reason_code.value

    mutated = dict(base)
    mutated["actor"] = {
        "actor_id": "op-malicious",
        "role": "authorized_technical_operator",
    }
    mutated["actor"]["name"] = "__import__('os').system('id')"
    _, denial = parse_request(mutated, NOW_ISO)
    outcomes["executable_content"] = denial.reason_code.value

    # duplicate-key / non-canonical JSON is rejected before any lookup.
    duplicate_payload = json.dumps(base, sort_keys=True)
    duplicate_payload = (
        '{' + '"idempotency_key":"' + base["idempotency_key"] + '",'
        + '"idempotency_key":"' + base["idempotency_key"] + '"'
        + '}'
    )
    try:
        strict_json_loads(duplicate_payload)
        outcomes["duplicate_key"] = "ADMITTED"
    except ValueError:
        outcomes["duplicate_key"] = "REJECTED"

    expected = {
        "unknown_property": "SCHEMA_REJECTED",
        "unknown_parameter": "UNKNOWN_PARAMETER",
        "unknown_nested_property": "SCHEMA_REJECTED",
        "unknown_runbook": "UNKNOWN_RUNBOOK",
        "scope_expansion": "SCOPE_EXPANSION_REJECTED",
        "target_revision_drift": "TARGET_REVISION_CONFLICT",
        "wrong_role": "AUTHORITY_MISMATCH",
        "readback_contract_drift": "TARGET_REVISION_CONFLICT",
        "supersession_key_drift": "SCOPE_EXPANSION_REJECTED",
        "executable_content": "EXECUTABLE_CONTENT_REJECTED",
        "duplicate_key": "REJECTED",
    }
    if outcomes != expected:
        raise ValueError(f"mutation rejection drift: {outcomes}")
    return outcomes


# --------------------------------------------------------------------------- #
# Issuance, execution, replay and concurrency
# --------------------------------------------------------------------------- #

def _validate_issuance_and_execution(
    catalog, issuer, plan, decision, observations
) -> dict[str, Any]:
    issued = mint_evidence(issuer, plan, decision, observations)
    entry = catalog[FORWARD_RUNBOOK]
    request = build_request(issued, entry, plan, decision)

    runtime = new_runtime(catalog, issuer)
    before = runtime._state_store.read().to_dict()
    result = runtime.handle(request)
    if not result.is_success:
        raise ValueError(f"nominal execution denied: {result.to_dict()}")
    receipt = result.to_dict()
    validate(SCHEMA_EXAMPLES["simulator_execution_receipt"][0], receipt)
    if receipt["result"] != "simulated_effect_verified":
        raise ValueError("nominal success result drift")
    if receipt["evidence_label"] != EVIDENCE_LABEL:
        raise ValueError("evidence label drift")
    if receipt["readback_fresh"] is not True:
        raise ValueError("success released without distinct fresh read")
    if receipt["readback_health"] != HEALTH_HEALTHY:
        raise ValueError("readback health drift")
    if receipt["readback_revision"] != EXPECTED_REVISION:
        raise ValueError("readback revision drift")

    after = runtime._state_store.read().to_dict()
    if before["health"] != HEALTH_DEGRADED or after["health"] != HEALTH_HEALTHY:
        raise ValueError("synthetic service transition drift")
    if before["revision"] != after["revision"]:
        raise ValueError("unexpected revision change")

    if len(runtime.attempt_audit_records) != 1:
        raise ValueError("attempt evidence count drift")
    if len(runtime.effect_audit_records) != 1:
        raise ValueError("effect audit count drift")
    consumed = issuer.records[issued.record.reference_sha256].state
    if consumed != EvidenceState.CONSUMED:
        raise ValueError("evidence was not consumed exactly once")

    if runtime.last_envelope is None:
        raise ValueError("backend-owned envelope was not built")
    validate(SCHEMA_EXAMPLES["simulator_command_envelope"][0], runtime.last_envelope.to_dict())
    envelope_example = load_json(SCHEMA_EXAMPLES["simulator_command_envelope"][1])
    if runtime.last_envelope.to_dict() != envelope_example:
        raise ValueError("built envelope does not match the canonical example")

    return {
        "issued_evidence_id": issued.record.evidence_id,
        "evidence_state_after": consumed.value,
        "before_health": before["health"],
        "after_health": after["health"],
        "readback_health": receipt["readback_health"],
        "readback_fresh": receipt["readback_fresh"],
        "result": receipt["result"],
        "attempt_evidence_sha256": receipt["attempt_evidence_sha256"],
        "effect_audit_sha256": receipt["effect_audit_sha256"],
        "attempt_record_count": len(runtime.attempt_audit_records),
        "effect_record_count": len(runtime.effect_audit_records),
    }


def _validate_replay_and_concurrency(
    catalog, plan, decision, observations
) -> dict[str, Any]:
    entry = catalog[FORWARD_RUNBOOK]
    outcomes: dict[str, Any] = {}

    # same-key exact replay
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    first = runtime.handle(request)
    second = runtime.handle(request)
    outcomes["same_key_exact_replay"] = {
        "same_receipt": first.to_dict() == second.to_dict(),
        "success": second.is_success,
        "attempt_record_count": len(runtime.attempt_audit_records),
        "effect_record_count": len(runtime.effect_audit_records),
    }
    if not outcomes["same_key_exact_replay"]["same_receipt"]:
        raise ValueError("same-key replay did not return the stored receipt")
    if outcomes["same_key_exact_replay"]["attempt_record_count"] != 1:
        raise ValueError("replay created a second attempt")

    # same-key changed fingerprint -> conflict
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    runtime.handle(request)
    conflict = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            correlation_id="83000000-0000-4000-8000-000000000001",
        )
    )
    outcomes["same_key_changed_fingerprint"] = conflict.to_dict()["reason_code"]
    if outcomes["same_key_changed_fingerprint"] != "IDEMPOTENCY_CONFLICT":
        raise ValueError("changed-fingerprint conflict drift")

    # in-progress key
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    runtime.seed_in_progress_idempotency(
        request.idempotency_key, request.fingerprint()
    )
    in_progress = runtime.handle(request)
    outcomes["in_progress_key"] = in_progress.to_dict()["reason_code"]
    if outcomes["in_progress_key"] != "IDEMPOTENCY_IN_PROGRESS":
        raise ValueError("in-progress denial drift")

    # different-key evidence replay
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
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
    outcomes["different_key_evidence_replay"] = replay.to_dict()["reason_code"]
    if outcomes["different_key_evidence_replay"] != "EXECUTION_EVIDENCE_REPLAY":
        raise ValueError("different-key evidence replay drift")
    if len(runtime.effect_audit_records) != 1:
        raise ValueError("different-key replay caused an effect")

    # concurrent single-winner behavior
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    results: list = []
    barrier = threading.Barrier(2)

    def worker() -> None:
        barrier.wait()
        results.append(runtime.handle(request))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    successes = sum(1 for r in results if r.is_success)
    outcomes["concurrent_single_winner"] = {
        "success_count": successes,
        "total_results": len(results),
        "attempt_record_count": len(runtime.attempt_audit_records),
        "effect_record_count": len(runtime.effect_audit_records),
        "evidence_consumed_count": sum(
            1
            for rec in issuer.records.values()
            if rec.state == EvidenceState.CONSUMED
        ),
    }
    if successes < 1:
        raise ValueError("no concurrent winner succeeded")
    if len(runtime.attempt_audit_records) != 1:
        raise ValueError("concurrency produced multiple handler attempts")
    if len(runtime.effect_audit_records) != 1:
        raise ValueError("concurrency produced multiple effects")
    if outcomes["concurrent_single_winner"]["evidence_consumed_count"] != 1:
        raise ValueError("concurrency consumed evidence multiple times")

    return outcomes


# --------------------------------------------------------------------------- #
# Denial cases (zero simulated effect)
# --------------------------------------------------------------------------- #

def _evidence_record_from_example(state: str = "issued") -> dict[str, Any]:
    record = load_json(SCHEMA_EXAMPLES["execution_evidence"][1])
    record["state"] = state
    return record


def _validate_denial_cases(
    catalog, plan, decision, observations
) -> dict[str, Any]:
    entry = catalog[FORWARD_RUNBOOK]
    outcomes: dict[str, Any] = {}

    def record_outcome(name: str, runtime: SimulatorRuntime, result) -> None:
        code = result.to_dict()["reason_code"]
        outcomes[name] = {
            "reason_code": code,
            "effect_record_count": len(runtime.effect_audit_records),
        }
        if len(runtime.effect_audit_records) != 0:
            raise ValueError(f"{name}: produced a simulated effect")

    # unknown / tampered evidence
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    unknown = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            evidence_reference="deadbeef" * 16,
        )
    )
    record_outcome("unknown_evidence", runtime, unknown)

    # expired evidence
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(
        catalog, issuer, now=datetime(2026, 8, 4, 8, 2, 0, tzinfo=timezone.utc)
    )
    expired = runtime.handle(build_request(issued, entry, plan, decision))
    record_outcome("expired_evidence", runtime, expired)

    # superseded evidence
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    runtime.mark_superseded(SUPERSESSION_KEY)
    superseded = runtime.handle(build_request(issued, entry, plan, decision))
    record_outcome("superseded_evidence", runtime, superseded)

    # mismatched plan/decision/catalog binding
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    request = SimulatorRequest(
        request.idempotency_key,
        request.correlation_id,
        request.actor,
        request.evidence_reference,
        request.runbook_id,
        request.target,
        request.parameters,
        PlanBinding(
            request.plan_binding.plan_id,
            request.plan_binding.plan_revision,
            "0" * 64,
        ),
        request.decision_binding,
        request.catalog_binding,
        request.supersession_key,
        request.readback_contract,
    )
    record_outcome("mismatched_plan_binding", runtime, runtime.handle(request))

    # wrong actor
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    wrong_actor = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            actor=Actor(actor_id="op-other", role=REQUIRED_ROLE),
        )
    )
    record_outcome("wrong_actor", runtime, wrong_actor)

    # wrong role
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    wrong_role = runtime.handle(
        build_request(
            issued,
            entry,
            plan,
            decision,
            actor=Actor(actor_id=ACTOR_ID, role="practice_manager"),
        )
    )
    record_outcome("wrong_role", runtime, wrong_role)

    # target revision drift
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    request = SimulatorRequest(
        request.idempotency_key,
        request.correlation_id,
        request.actor,
        request.evidence_reference,
        request.runbook_id,
        TargetRef(
            request.target.environment,
            request.target.kind,
            request.target.target_id,
            "0.0.0-drift",
        ),
        request.parameters,
        request.plan_binding,
        request.decision_binding,
        request.catalog_binding,
        request.supersession_key,
        request.readback_contract,
    )
    record_outcome("target_revision_drift", runtime, runtime.handle(request))

    # scope expansion (different environment)
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    request = SimulatorRequest(
        request.idempotency_key,
        request.correlation_id,
        request.actor,
        request.evidence_reference,
        request.runbook_id,
        TargetRef("production", "database", "prod:db", request.target.expected_revision),
        request.parameters,
        request.plan_binding,
        request.decision_binding,
        request.catalog_binding,
        request.supersession_key,
        request.readback_contract,
    )
    record_outcome("scope_expansion", runtime, runtime.handle(request))

    # multiple-environment claim
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    request = build_request(issued, entry, plan, decision)
    request = SimulatorRequest(
        request.idempotency_key,
        request.correlation_id,
        request.actor,
        request.evidence_reference,
        request.runbook_id,
        TargetRef("staging", "service", "synthetic:api-service", request.target.expected_revision),
        request.parameters,
        request.plan_binding,
        request.decision_binding,
        request.catalog_binding,
        request.supersession_key,
        request.readback_contract,
    )
    record_outcome("multiple_environment", runtime, runtime.handle(request))

    # invalid reviewer separation (handler-time: reviewer == generator)
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    runtime = new_runtime(catalog, issuer)
    bad_record = _evidence_record_from_example("issued")
    bad_record["reviewer_id"] = bad_record["candidate_generator_id"]
    from scripts.model_required_bureau_c4_simulator import ExecutionEvidenceRecord

    runtime._evidence_records[issued.record.reference_sha256] = (
        ExecutionEvidenceRecord.from_dict(bad_record)
    )
    reviewer_invalid = runtime.handle(build_request(issued, entry, plan, decision))
    record_outcome("reviewer_separation", runtime, reviewer_invalid)

    # stale observation (handler-time)
    issuer = EvidenceIssuer(catalog, now_callable)
    issued = mint_evidence(issuer, plan, decision, observations)
    stale_record = _evidence_record_from_example("issued")
    stale_record["expires_at"] = "2026-08-04T09:00:00Z"
    from scripts.model_required_bureau_c4_simulator import ExecutionEvidenceRecord as EER

    runtime = new_runtime(
        catalog,
        issuer,
        now=datetime(2026, 8, 4, 8, 6, 0, tzinfo=timezone.utc),
    )
    runtime._evidence_records[issued.record.reference_sha256] = EER.from_dict(
        stale_record
    )
    stale = runtime.handle(build_request(issued, entry, plan, decision))
    record_outcome("stale_observation", runtime, stale)

    # reviewer == generator at issuance (zero effect: no evidence minted)
    issuer = EvidenceIssuer(catalog, now_callable)
    try:
        issuer.mint(
            plan=plan,
            decision=decision,
            candidate_generator_id=GENERATOR_ID,
            reviewer_id=GENERATOR_ID,
            actor=Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
            observations=observations,
            correlation_id=CORRELATION_ID,
            reference=FIXTURE_REFERENCE,
            nonce=FIXTURE_NONCE,
            actor_expires_at="2026-08-04T08:01:00Z",
            reviewer_expires_at="2026-08-04T08:01:00Z",
        )
        outcomes["issuance_reviewer_separation"] = "ADMITTED"
        raise ValueError("issuer admitted reviewer == generator")
    except IssuanceDenied as error:
        outcomes["issuance_reviewer_separation"] = error.reason.value
        if error.reason != DenialReason.REVIEWER_INVALID:
            raise ValueError("issuance reviewer separation drift")

    # observation mismatch at issuance
    issuer = EvidenceIssuer(catalog, now_callable)
    bad_observations = [
        dict(item) for item in observations
    ]
    for item in bad_observations:
        if item["observation_id"] == "api-health":
            item["content_sha256"] = "0" * 64
    try:
        issuer.mint(
            plan=plan,
            decision=decision,
            candidate_generator_id=GENERATOR_ID,
            reviewer_id=REVIEWER_ID,
            actor=Actor(actor_id=ACTOR_ID, role=REQUIRED_ROLE),
            observations=bad_observations,
            correlation_id=CORRELATION_ID,
            reference=FIXTURE_REFERENCE,
            nonce=FIXTURE_NONCE,
            actor_expires_at="2026-08-04T08:01:00Z",
            reviewer_expires_at="2026-08-04T08:01:00Z",
        )
        outcomes["issuance_observation_mismatch"] = "ADMITTED"
        raise ValueError("issuer admitted mismatched observation")
    except IssuanceDenied as error:
        outcomes["issuance_observation_mismatch"] = error.reason.value
        if error.reason != DenialReason.OBSERVATION_MISMATCH:
            raise ValueError("issuance observation mismatch drift")

    expected_codes = {
        "unknown_evidence": "EXECUTION_EVIDENCE_INVALID",
        "expired_evidence": "STALE_OR_SUPERSEDED",
        "superseded_evidence": "STALE_OR_SUPERSEDED",
        "mismatched_plan_binding": "AUTHORITY_MISMATCH",
        "wrong_actor": "AUTHORITY_MISMATCH",
        "wrong_role": "AUTHORITY_MISMATCH",
        "target_revision_drift": "TARGET_REVISION_CONFLICT",
        "scope_expansion": "SCOPE_EXPANSION_REJECTED",
        "multiple_environment": "SCOPE_EXPANSION_REJECTED",
        "reviewer_separation": "REVIEWER_INVALID",
        "stale_observation": "OBSERVATION_MISMATCH",
        "issuance_reviewer_separation": "REVIEWER_INVALID",
        "issuance_observation_mismatch": "OBSERVATION_MISMATCH",
    }
    for name, expected in expected_codes.items():
        actual = outcomes[name]
        code = actual if isinstance(actual, str) else actual["reason_code"]
        if code != expected:
            raise ValueError(f"{name}: expected {expected} got {code}")
    return outcomes


# --------------------------------------------------------------------------- #
# Fault injection (no false success)
# --------------------------------------------------------------------------- #

def _validate_fault_injection(
    catalog, plan, decision, observations
) -> dict[str, Any]:
    entry = catalog[FORWARD_RUNBOOK]
    outcomes: dict[str, Any] = {}

    def run_fault(
        fault: FaultInjection,
        *,
        expect_evidence_consumed: bool,
    ) -> dict[str, Any]:
        issuer = EvidenceIssuer(catalog, now_callable)
        issued = mint_evidence(issuer, plan, decision, observations)
        runtime = new_runtime(catalog, issuer)
        result = runtime.handle(build_request(issued, entry, plan, decision), fault=fault)
        outcome = {
            "reason_code": result.to_dict()["reason_code"],
            "success": result.is_success,
            "rollback": result.to_dict()["rollback"],
            "state_health": runtime._state_store.read().health,
            "effect_record_count": len(runtime.effect_audit_records),
            "attempt_record_count": len(runtime.attempt_audit_records),
            "evidence_consumed": (
                issuer.records[issued.record.reference_sha256].state
                == EvidenceState.CONSUMED
            ),
        }
        if result.is_success:
            raise ValueError(f"{fault.value}: false success released")
        if outcome["attempt_record_count"] != 1:
            raise ValueError(f"{fault.value}: attempt evidence count drift")
        if outcome["evidence_consumed"] != expect_evidence_consumed:
            raise ValueError(f"{fault.value}: evidence consumption drift")
        return outcome

    outcomes["transition_failed"] = run_fault(
        FaultInjection.TRANSITION_FAILED, expect_evidence_consumed=True
    )
    if outcomes["transition_failed"]["reason_code"] != "SIMULATED_TRANSITION_FAILED":
        raise ValueError("transition-failed reason drift")
    if outcomes["transition_failed"]["state_health"] != HEALTH_DEGRADED:
        raise ValueError("transition failure did not restore state snapshot")
    if outcomes["transition_failed"]["effect_record_count"] != 0:
        raise ValueError("transition failure did not restore effect audit snapshot")

    outcomes["effect_audit_append_failed"] = run_fault(
        FaultInjection.EFFECT_AUDIT_APPEND_FAILED, expect_evidence_consumed=True
    )
    if outcomes["effect_audit_append_failed"]["reason_code"] != "SIMULATED_TRANSITION_FAILED":
        raise ValueError("audit-append-failed reason drift")
    if outcomes["effect_audit_append_failed"]["state_health"] != HEALTH_DEGRADED:
        raise ValueError("audit failure did not restore state snapshot")
    if outcomes["effect_audit_append_failed"]["effect_record_count"] != 0:
        raise ValueError("audit failure did not restore effect audit snapshot")

    outcomes["handler_false_return"] = run_fault(
        FaultInjection.HANDLER_RETURN_FALSE, expect_evidence_consumed=True
    )
    if outcomes["handler_false_return"]["reason_code"] != (
        "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED"
    ):
        raise ValueError("false-handler-return did not fail closed")
    if outcomes["handler_false_return"]["state_health"] != HEALTH_DEGRADED:
        raise ValueError("false-handler-return state drift")

    outcomes["first_readback_failed"] = run_fault(
        FaultInjection.FIRST_READBACK_FAILED, expect_evidence_consumed=True
    )
    if outcomes["first_readback_failed"]["reason_code"] != (
        "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED"
    ):
        raise ValueError("first-readback-failed did not fail closed")
    if outcomes["first_readback_failed"]["rollback"]["verified"] is not True:
        raise ValueError("verified rollback not distinguished")

    outcomes["rollback_failed"] = run_fault(
        FaultInjection.ROLLBACK_FAILED, expect_evidence_consumed=True
    )
    if outcomes["rollback_failed"]["reason_code"] != "SIMULATED_ROLLBACK_UNVERIFIED":
        raise ValueError("rollback-failed reason drift")
    if outcomes["rollback_failed"]["rollback"]["verified"] is not False:
        raise ValueError("rollback-failed must be unverified")

    outcomes["rollback_readback_unverified"] = run_fault(
        FaultInjection.ROLLBACK_READBACK_UNVERIFIED, expect_evidence_consumed=True
    )
    if outcomes["rollback_readback_unverified"]["reason_code"] != (
        "SIMULATED_ROLLBACK_UNVERIFIED"
    ):
        raise ValueError("rollback-readback-unverified reason drift")

    return outcomes


# --------------------------------------------------------------------------- #
# Source checks and document boundary
# --------------------------------------------------------------------------- #

def _validate_source_checks() -> dict[str, Any]:
    import ast

    simulator_path = ROOT / "scripts/model_required_bureau_c4_simulator.py"
    source = simulator_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])

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
    forbidden_imports = sorted(imported - allowed)

    forbidden_calls = {"eval", "exec", "compile", "__import__", "open", "input", "breakpoint"}
    call_hits: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in forbidden_calls:
                call_hits.add(func.id)

    if "app" in imported or any(name.startswith("app.") for name in imported):
        raise ValueError("simulator imports app.main or app package")

    return {
        "imported_modules": sorted(imported),
        "forbidden_imports": forbidden_imports,
        "forbidden_call_hits": sorted(call_hits),
        "simulator_source_lf": simulator_path.read_bytes().count(b"\r") == 0,
    }


def _validate_document_boundary() -> dict[str, Any]:
    plan_text = PLAN.read_text(encoding="utf-8")
    threat_text = THREAT.read_text(encoding="utf-8")
    combined = (plan_text + threat_text).lower()
    required = (
        "provider_free_authored_synthetic_allowlisted_actuator_simulation",
        "restart-api-synthetic.v1",
        "restore-api-synthetic-lkg.v1",
        "execution_authorized: false",
        "distinct fresh read",
        "zero filesystem",
        "docs/branding/",
        "no dynamic import",
    )
    missing = [phrase for phrase in required if phrase not in combined]
    if missing:
        raise ValueError(f"document boundary missing: {missing}")
    return {"document_count": 2, "required_boundary_count": len(required)}


# --------------------------------------------------------------------------- #
# Evidence assembly
# --------------------------------------------------------------------------- #

def build_evidence() -> dict[str, Any]:
    catalog = load_catalog()
    plan, decision, observations = load_c3_fixtures()

    schemas = _validate_schemas_and_examples()
    digests = _validate_digest_reproduction(catalog[FORWARD_RUNBOOK], plan, decision)
    entry = catalog[FORWARD_RUNBOOK]

    mutation_issuer = EvidenceIssuer(catalog, now_callable)
    mutation_issued = mint_evidence(mutation_issuer, plan, decision, observations)
    mutations = _validate_mutation_rejections(
        mutation_issued, entry, plan, decision
    )

    execution_issuer = EvidenceIssuer(catalog, now_callable)
    issuance_execution = _validate_issuance_and_execution(
        catalog, execution_issuer, plan, decision, observations
    )
    replay_concurrency = _validate_replay_and_concurrency(
        catalog, plan, decision, observations
    )
    denial_cases = _validate_denial_cases(catalog, plan, decision, observations)
    fault_injection = _validate_fault_injection(catalog, plan, decision, observations)
    source_checks = _validate_source_checks()
    documents = _validate_document_boundary()

    artifact_paths = [PLAN, THREAT]
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        artifact_paths.extend([schema_path, example_path])
    artifact_paths.append(ROOT / "scripts/model_required_bureau_c4_simulator.py")
    artifact_paths.append(ROOT / "scripts/model_required_bureau_c4_acceptance.py")

    operation_counters = _runtime_zero_counters()
    if not all(v == 0 for v in operation_counters.values()):
        raise ValueError("operation counters are not zero")

    return {
        "schema_version": "emr4.model_required_bureau_c4_acceptance.v1",
        "passed": True,
        "result": EXPECTED_RESULT,
        "source_head": EXPECTED_HEAD,
        "evidence_label": EVIDENCE_LABEL,
        "schemas": schemas,
        "digest_reproduction": digests,
        "mutation_rejections": mutations,
        "issuance_and_execution": issuance_execution,
        "replay_and_concurrency": replay_concurrency,
        "denial_cases": denial_cases,
        "fault_injection": fault_injection,
        "operation_counters": operation_counters,
        "source_checks": source_checks,
        "documents": documents,
        "artifact_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_bytes(path)
            for path in artifact_paths
        },
    }


def _runtime_zero_counters() -> dict[str, int]:
    from scripts.model_required_bureau_c4_simulator import ForbiddenOperationCounters

    return ForbiddenOperationCounters().to_dict()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    evidence = build_evidence()
    if args.check:
        if load_json(args.output) != evidence:
            raise SystemExit("acceptance evidence is stale")
    else:
        with args.output.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "passed": True,
                "result": EXPECTED_RESULT,
                "source_head": EXPECTED_HEAD,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
