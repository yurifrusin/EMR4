"""Provider-free private-shadow clockwork shared by Ariadne and broker rehearsals."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, NoReturn


ZERO_DIGEST = "0" * 64
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_EVENT_KINDS = (
    "ariadne_request_admitted",
    "broker_work_order_leased",
    "broker_terminal_result",
    "ariadne_terminal_acknowledged",
)
EXPECTED_READING_SOURCES = {
    "live_operation_latch",
    "stage_catalogue",
    "git_and_protected_refs",
    "source_bindings",
    "failure_gauge_ledger",
    "genesis_or_previous_acknowledged_tip",
}


class ClockworkRejection(ValueError):
    """An invalid reading or gear state rejected before publication."""

    def __init__(self, phase: str, rule: str) -> None:
        super().__init__(f"{phase}:{rule}")
        self.phase = phase
        self.rule = rule


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_lf_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ClockworkRejection("reading", "json_object_required")
    return value


def load_json_value(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _reject(phase: str, rule: str) -> NoReturn:
    raise ClockworkRejection(phase, rule)


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def validate_contract(contract: object) -> dict[str, Any]:
    if not isinstance(contract, dict):
        _reject("reading", "contract_object")
    required = {
        "schema_version",
        "operation_id",
        "planning_source",
        "accepted_architecture_source",
        "task_branch",
        "protected_ref_oid",
        "stage_catalogue",
        "source_bindings",
        "reading_sources",
        "caller_supplied_binding_fields",
        "engine_owned_fields",
        "policy",
        "publication",
        "efficacy",
        "closed_surfaces",
    }
    if set(contract) != required:
        _reject("reading", "contract_key_set")
    if contract["schema_version"] != "ariadne.shadow_clockwork_rehearsal_contract.v1":
        _reject("reading", "contract_schema")
    for field in ("planning_source", "accepted_architecture_source", "protected_ref_oid"):
        if not isinstance(contract[field], str) or not GIT_OID.fullmatch(contract[field]):
            _reject("reading", f"full_git_oid_{field}")
    if contract["caller_supplied_binding_fields"] != []:
        _reject("request", "caller_binding_field")
    if len(contract["engine_owned_fields"]) != 15:
        _reject("reading", "engine_field_inventory")
    if set(contract["reading_sources"]) != EXPECTED_READING_SOURCES:
        _reject("reading", "reading_inventory_incomplete")
    policy = contract["policy"]
    if not isinstance(policy, dict):
        _reject("reading", "policy_object")
    required_policy = {
        "admitted_effect_class": "shadow_generation_write",
        "profile_family": "emr4-provider-free",
        "permission_preset": "provider-free-shadow-read-generate",
        "minimized_tools": ["read", "generate_private_shadow"],
        "automatic_retries": 0,
        "silent_fallbacks": 0,
        "provider_calls": 0,
        "single_writer": True,
        "one_terminal_result": True,
        "acknowledgement_required": True,
        "raw_prompt_reasoning_secret_or_product_payload_allowed": False,
        "worker_self_acceptance_allowed": False,
        "live_adoption": False,
    }
    for key, expected in required_policy.items():
        if policy.get(key) != expected:
            _reject("reading", f"policy_{key}")
    publication = contract["publication"]
    if publication.get("mode") != "private_shadow_generation_atomic_rename":
        _reject("publication", "publication_mode")
    efficacy = contract["efficacy"]
    expected_efficacy = {
        "comparator_failure_induced_reruns": 14,
        "maximum_candidate_failure_induced_reruns": 7,
        "required_failure_gauge_coverage": 14,
        "caller_supplied_derived_fields": 0,
        "new_mutable_current_fixtures": 0,
        "partial_publications": 0,
        "uncaught_escapes": 0,
        "coverage_loss": False,
        "timing_acceptance_relevant": False,
        "report_shared_engine_growth": True,
        "report_clean_run_overhead": True,
    }
    if efficacy != expected_efficacy:
        _reject("efficacy", "thresholds")
    return contract


def verify_source_bindings(repo_root: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    verified: list[dict[str, str]] = []
    paths: set[str] = set()
    for binding in contract["source_bindings"]:
        if not isinstance(binding, dict) or set(binding) != {"path", "canonical_lf_sha256"}:
            _reject("reading", "source_binding_shape")
        relative = binding["path"]
        expected = binding["canonical_lf_sha256"]
        if not isinstance(relative, str) or relative in paths:
            _reject("reading", "source_binding_path")
        path = repo_root / relative
        if not path.is_file():
            _reject("reading", "unmaterialized_path")
        actual = canonical_lf_sha256(path)
        if not isinstance(expected, str) or not SHA256.fullmatch(expected) or actual != expected:
            _reject("reading", "source_binding_digest")
        paths.add(relative)
        verified.append({"path": relative, "canonical_lf_sha256": actual})
    if len(verified) != 11:
        _reject("reading", "source_binding_count")
    return verified


def validate_latch(latch: object, contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(latch, dict):
        _reject("reading", "latch_object")
    if latch.get("schema_version") != "ariadne.active_operation_latch.v1":
        _reject("reading", "latch_schema")
    if latch.get("operation_id") != contract["operation_id"]:
        _reject("reading", "latch_operation")
    status = latch.get("status")
    if status not in contract["stage_catalogue"]:
        _reject("reading", "latch_status")
    source_head = latch.get("source_head")
    if not isinstance(source_head, str) or not GIT_OID.fullmatch(source_head):
        _reject("reading", "latch_full_source_oid")
    if not isinstance(latch.get("protected_boundaries"), list):
        _reject("reading", "latch_boundaries")
    terminal = latch.get("terminal_response")
    if not isinstance(terminal, dict) or not isinstance(terminal.get("permitted"), bool):
        _reject("reading", "latch_terminal_shape")
    return latch


def derive_git_snapshot(repo_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    refs = {
        "head": _git(repo_root, "rev-parse", "HEAD"),
        "master": _git(repo_root, "rev-parse", "master"),
        "origin_master": _git(repo_root, "rev-parse", "origin/master"),
        "handoff_current": _git(repo_root, "rev-parse", "handoff/current"),
        "origin_handoff_current": _git(repo_root, "rev-parse", "origin/handoff/current"),
    }
    if any(not GIT_OID.fullmatch(oid) for oid in refs.values()):
        _reject("request", "full_git_oid")
    protected = contract["protected_ref_oid"]
    if any(refs[key] != protected for key in refs if key != "head"):
        _reject("request", "protected_ref_drift")
    branch = _git(repo_root, "branch", "--show-current")
    if branch != contract["task_branch"]:
        _reject("request", "task_branch")
    return {
        "branch": branch,
        "refs": refs,
        "branch_and_protected_ref_digest": digest({"branch": branch, "refs": refs}),
    }


def validate_failure_gauges(value: object) -> list[dict[str, str]]:
    if not isinstance(value, dict):
        _reject("reading", "gauge_ledger_object")
    if value.get("schema_version") != "ariadne.shadow_clockwork_failure_gauges.v1":
        _reject("reading", "gauge_ledger_schema")
    if value.get("comparator_failure_induced_reruns") != 14:
        _reject("efficacy", "comparator_reruns")
    gauges = value.get("gauges")
    if not isinstance(gauges, list) or len(gauges) != 14:
        _reject("efficacy", "failure_gauge_count")
    expected_keys = {"id", "incident", "rejection_rule", "expected_phase", "covered_control"}
    ids: set[str] = set()
    rules: set[str] = set()
    for gauge in gauges:
        if not isinstance(gauge, dict) or set(gauge) != expected_keys:
            _reject("reading", "failure_gauge_shape")
        if gauge["id"] in ids or gauge["rejection_rule"] in rules:
            _reject("reading", "failure_gauge_unique")
        if gauge["expected_phase"] not in {"reading", "request", "work_order", "projection"}:
            _reject("reading", "failure_gauge_phase")
        ids.add(gauge["id"])
        rules.add(gauge["rejection_rule"])
    if rules != set(_GAUGE_FAULTS):
        _reject("reading", "failure_gauge_rule_inventory")
    return gauges


def _event(sequence: int, kind: str, writer: str, previous: str, payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "sequence": sequence,
        "kind": kind,
        "writer": writer,
        "previous_event_sha256": previous,
        "payload": payload,
    }
    event["event_sha256"] = digest(event)
    return event


def _derive_generation(
    repo_root: Path,
    contract: dict[str, Any],
    latch: dict[str, Any],
    source_bindings: list[dict[str, str]],
    gauges: list[dict[str, str]],
) -> dict[str, Any]:
    git = derive_git_snapshot(repo_root, contract)
    evidence_digest = digest(source_bindings)
    gauge_digest = digest(gauges)
    policy_digest = digest(contract["policy"])
    forbidden_digest = digest(contract["closed_surfaces"])
    stage_id = contract["stage_catalogue"][latch["status"]]
    retry_counters = {
        key: int(value)
        for key, value in latch["checkpoint"]["retry_counters"].items()
    }
    attempt_ordinal = sum(retry_counters.values()) + 1
    attempt_id = digest(
        {
            "operation_id": latch["operation_id"],
            "source_commit": git["refs"]["head"],
            "stage_id": stage_id,
            "attempt_ordinal": attempt_ordinal,
        }
    )
    common = {
        "operation_id": latch["operation_id"],
        "stage_id": stage_id,
        "effect_class": contract["policy"]["admitted_effect_class"],
        "source_commit": git["refs"]["head"],
        "branch_and_protected_ref_digest": git["branch_and_protected_ref_digest"],
        "attempt_id": attempt_id,
        "attempt_ordinal": attempt_ordinal,
        "workflow_retry_counters_sha256": digest(retry_counters),
        "source_binding_digest": evidence_digest,
        "failure_gauge_digest": gauge_digest,
        "policy_digest": policy_digest,
        "forbidden_surface_digest": forbidden_digest,
    }
    request = _event(1, EXPECTED_EVENT_KINDS[0], "ariadne", ZERO_DIGEST, {**common, "disposition": "admitted"})
    work_order_body = {
        **common,
        "parent_event_sha256": request["event_sha256"],
        "leased_sequence": 2,
        "lease_from": "ariadne",
        "lease_to": "deepseek_broker",
        "branch": git["branch"],
        "worktree": str(repo_root.resolve()),
        "profile_family": contract["policy"]["profile_family"],
        "permission_preset": contract["policy"]["permission_preset"],
        "package": contract["policy"]["native_harness_package"],
        "package_version": contract["policy"]["native_harness_version"],
        "tool_view": contract["policy"]["minimized_tools"],
        "automatic_retries": 0,
        "silent_fallbacks": 0,
        "occupied_enabled": False,
    }
    work_order_body["work_order_sha256"] = digest(work_order_body)
    leased = _event(2, EXPECTED_EVENT_KINDS[1], "ariadne", request["event_sha256"], work_order_body)
    terminal_body = {
        **common,
        "work_order_sha256": work_order_body["work_order_sha256"],
        "lease_event_sha256": leased["event_sha256"],
        "session_identity_sha256": digest({"attempt_id": attempt_id, "broker": "provider_free_simulation"}),
        "provider_call_count": 0,
        "ordered_tool_result_sha256": digest(["read", "generate_private_shadow"]),
        "candidate_tree_diff_sha256": digest({"candidate_write": False}),
        "test_result_sha256": digest({"gauges": 14, "expected_rejections": 14}),
        "cleanup_state": "no_process_no_credential_no_provider",
        "terminal_class": "succeeded",
        "worker_self_accepted": False,
    }
    terminal = _event(3, EXPECTED_EVENT_KINDS[2], "deepseek_broker", leased["event_sha256"], terminal_body)
    acknowledgement_body = {
        **common,
        "terminal_event_sha256": terminal["event_sha256"],
        "terminal_class": terminal_body["terminal_class"],
        "lease_from": "deepseek_broker",
        "lease_to": "ariadne",
        "disposition": "acknowledged",
    }
    acknowledgement = _event(4, EXPECTED_EVENT_KINDS[3], "ariadne", terminal["event_sha256"], acknowledgement_body)
    journal = [request, leased, terminal, acknowledgement]
    tip = acknowledgement["event_sha256"]
    projections = {
        name: {"acknowledged_tip_sha256": tip, "revision": 1}
        for name in ("continuity", "compass", "report", "latch", "incident", "broker")
    }
    work_order = {**work_order_body, "lease_event_sha256": leased["event_sha256"]}
    terminal_result = {**terminal_body, "terminal_event_sha256": terminal["event_sha256"]}
    acknowledgement_record = {**acknowledgement_body, "acknowledgement_event_sha256": tip}
    return {
        "schema_version": "ariadne.shadow_clockwork_generation.v1",
        "journal": journal,
        "work_order": work_order,
        "terminal_result": terminal_result,
        "acknowledgement": acknowledgement_record,
        "projections": projections,
        "readings": {
            "source_bindings": source_bindings,
            "git": git,
            "latch_shape": {
                "schema_version": latch["schema_version"],
                "status": latch["status"],
                "source_oid_is_full": bool(GIT_OID.fullmatch(latch["source_head"])),
                "terminal_permitted": latch["terminal_response"]["permitted"],
            },
            "failure_gauge_digest": gauge_digest,
            "workflow_retry_counters": retry_counters,
        },
    }


def validate_generation(generation: object, contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(generation, dict):
        _reject("projection", "generation_object")
    required = {"schema_version", "journal", "work_order", "terminal_result", "acknowledgement", "projections", "readings"}
    if set(generation) != required or generation["schema_version"] != "ariadne.shadow_clockwork_generation.v1":
        _reject("projection", "generation_shape")
    journal = generation["journal"]
    if not isinstance(journal, list) or len(journal) != 4:
        _reject("work_order", "one_terminal_result")
    previous = ZERO_DIGEST
    writers = ("ariadne", "ariadne", "deepseek_broker", "ariadne")
    for index, event in enumerate(journal, 1):
        if not isinstance(event, dict) or set(event) != {"sequence", "kind", "writer", "previous_event_sha256", "payload", "event_sha256"}:
            _reject("work_order", "event_shape")
        if event["sequence"] != index:
            _reject("work_order", "sequence_gap")
        if event["kind"] != EXPECTED_EVENT_KINDS[index - 1]:
            _reject("work_order", "event_kind")
        if event["writer"] != writers[index - 1]:
            _reject("work_order", "concurrent_writer")
        if event["previous_event_sha256"] != previous:
            _reject("work_order", "stale_parent")
        unhashed = {key: value for key, value in event.items() if key != "event_sha256"}
        if event["event_sha256"] != digest(unhashed):
            _reject("work_order", "event_digest")
        previous = event["event_sha256"]
    request, leased, terminal, ack = journal
    retry_counters = generation["readings"].get("workflow_retry_counters")
    if not isinstance(retry_counters, dict):
        _reject("request", "retry_counter_reading")
    if request["payload"].get("workflow_retry_counters_sha256") != digest(retry_counters):
        _reject("request", "retry_counter_binding")
    if request["payload"].get("attempt_ordinal") != sum(retry_counters.values()) + 1:
        _reject("request", "attempt_ordinal_binding")
    if leased["payload"]["parent_event_sha256"] != request["event_sha256"]:
        _reject("work_order", "lease_parent")
    work_order = generation["work_order"]
    work_order_body = {key: value for key, value in work_order.items() if key not in {"work_order_sha256", "lease_event_sha256"}}
    if work_order.get("work_order_sha256") != digest(work_order_body):
        _reject("work_order", "resource_digest_mismatch")
    if work_order.get("lease_event_sha256") != leased["event_sha256"]:
        _reject("work_order", "lease_event_binding")
    if work_order.get("occupied_enabled") or work_order.get("automatic_retries") != 0 or work_order.get("silent_fallbacks") != 0:
        _reject("work_order", "provider_or_fallback_open")
    if work_order.get("tool_view") != contract["policy"]["minimized_tools"]:
        _reject("work_order", "tool_view")
    terminal_result = generation["terminal_result"]
    if terminal_result.get("work_order_sha256") != work_order["work_order_sha256"]:
        _reject("work_order", "terminal_work_order_binding")
    if terminal_result.get("lease_event_sha256") != leased["event_sha256"]:
        _reject("work_order", "terminal_lease_binding")
    if terminal_result.get("provider_call_count") != 0:
        _reject("work_order", "provider_call")
    if terminal_result.get("worker_self_accepted"):
        _reject("work_order", "worker_self_acceptance")
    if terminal_result.get("terminal_event_sha256") != terminal["event_sha256"]:
        _reject("work_order", "terminal_event_binding")
    acknowledgement = generation["acknowledgement"]
    if acknowledgement.get("terminal_event_sha256") != terminal["event_sha256"]:
        _reject("work_order", "ack_terminal_binding")
    if acknowledgement.get("acknowledgement_event_sha256") != ack["event_sha256"]:
        _reject("work_order", "ack_event_binding")
    if acknowledgement.get("lease_from") != "deepseek_broker" or acknowledgement.get("lease_to") != "ariadne":
        _reject("work_order", "lease_not_returned")
    projections = generation["projections"]
    if not isinstance(projections, dict) or set(projections) != {"continuity", "compass", "report", "latch", "incident", "broker"}:
        _reject("projection", "projection_inventory")
    for projection in projections.values():
        if projection != {"acknowledged_tip_sha256": ack["event_sha256"], "revision": 1}:
            _reject("projection", "projection_tip")
    return generation


def _candidate_reading(generation: dict[str, Any]) -> dict[str, Any]:
    return {
        "mutable_current_literal": None,
        "projection_line_count": 498,
        "caller_binding_fields": [],
        "aggregate_population": 14,
        "recurrence_population": 2,
        "recurrence_residual_population": 12,
        "materialized_path": "docs/ariadne-agent-error-correction-register-revision-531.md",
        "source_oid": generation["journal"][0]["payload"]["source_commit"],
        "expected_source_oid": generation["journal"][0]["payload"]["source_commit"],
        "resource_digest": generation["work_order"]["work_order_sha256"],
        "expected_resource_digest": generation["work_order"]["work_order_sha256"],
        "standalone_population": 14,
        "typed_command": {"executable": "rg", "directory": "docs", "glob": "*.md"},
        "reading_inventory": sorted(EXPECTED_READING_SOURCES),
        "register_path_materialized": True,
        "latch_path_materialized": True,
        "lifecycle_source": generation["journal"][0]["payload"]["source_commit"],
        "expected_lifecycle_source": generation["journal"][0]["payload"]["source_commit"],
    }


_GAUGE_FAULTS: dict[str, tuple[str, str, object]] = {
    "mutable_current_literal": ("reading", "mutable_current_literal", "copied-live-stage"),
    "projection_limit": ("projection", "projection_line_count", 501),
    "caller_binding_field": ("request", "caller_binding_fields", ["source_commit"]),
    "aggregate_mismatch": ("projection", "aggregate_population", 13),
    "recurrence_mismatch": ("projection", "recurrence_residual_population", 11),
    "unmaterialized_path": ("reading", "materialized_path", "docs/guessed-yuri-summary.md"),
    "stale_source_oid": ("request", "source_oid", "27101fa"),
    "resource_digest_mismatch": ("work_order", "resource_digest", "f" * 64),
    "standalone_population_mismatch": ("projection", "standalone_population", 13),
    "untyped_command_operand": ("work_order", "typed_command", {"executable": "rg", "path": "docs/*.md"}),
    "reading_inventory_incomplete": ("reading", "reading_inventory", sorted(EXPECTED_READING_SOURCES - {"git_and_protected_refs"})),
    "unmaterialized_register_path": ("reading", "register_path_materialized", False),
    "unmaterialized_latch_path": ("reading", "latch_path_materialized", False),
    "lifecycle_source_mismatch": ("projection", "lifecycle_source", "0" * 40),
}


def validate_candidate_reading(candidate: dict[str, Any]) -> None:
    if candidate["mutable_current_literal"] is not None:
        _reject("reading", "mutable_current_literal")
    if candidate["projection_line_count"] > 500:
        _reject("projection", "projection_limit")
    if candidate["caller_binding_fields"]:
        _reject("request", "caller_binding_field")
    if candidate["aggregate_population"] != 14:
        _reject("projection", "aggregate_mismatch")
    if candidate["recurrence_population"] + candidate["recurrence_residual_population"] != 14:
        _reject("projection", "recurrence_mismatch")
    if candidate["materialized_path"] != "docs/ariadne-agent-error-correction-register-revision-531.md":
        _reject("reading", "unmaterialized_path")
    if not isinstance(candidate["source_oid"], str) or not GIT_OID.fullmatch(candidate["source_oid"]):
        _reject("request", "stale_source_oid")
    if candidate["source_oid"] != candidate["expected_source_oid"]:
        _reject("request", "stale_source_oid")
    if candidate["resource_digest"] != candidate["expected_resource_digest"]:
        _reject("work_order", "resource_digest_mismatch")
    if candidate["standalone_population"] != candidate["aggregate_population"]:
        _reject("projection", "standalone_population_mismatch")
    if set(candidate["typed_command"]) != {"executable", "directory", "glob"}:
        _reject("work_order", "untyped_command_operand")
    if set(candidate["reading_inventory"]) != EXPECTED_READING_SOURCES:
        _reject("reading", "reading_inventory_incomplete")
    if not candidate["register_path_materialized"]:
        _reject("reading", "unmaterialized_register_path")
    if not candidate["latch_path_materialized"]:
        _reject("reading", "unmaterialized_latch_path")
    if candidate["lifecycle_source"] != candidate["expected_lifecycle_source"]:
        _reject("projection", "lifecycle_source_mismatch")


def exercise_failure_gauges(generation: dict[str, Any], gauges: list[dict[str, str]]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for gauge in gauges:
        rule = gauge["rejection_rule"]
        expected_phase, field, bad_value = _GAUGE_FAULTS[rule]
        candidate = _candidate_reading(generation)
        candidate[field] = copy.deepcopy(bad_value)
        try:
            validate_candidate_reading(candidate)
        except ClockworkRejection as exc:
            if exc.rule != rule or exc.phase != expected_phase or exc.phase != gauge["expected_phase"]:
                _reject("efficacy", "failure_gauge_wrong_rejection")
            results.append({"id": gauge["id"], "rule": rule, "phase": exc.phase, "result": "rejected_before_publication"})
        else:
            _reject("efficacy", "failure_gauge_escape")
    validate_candidate_reading(_candidate_reading(generation))
    return results


def calculate_efficacy(
    contract: dict[str, Any],
    generation: dict[str, Any],
    gauge_results: list[dict[str, str]],
    *,
    line_growth: dict[str, int],
    clean_run_overhead_ms: float,
) -> dict[str, Any]:
    comparator = contract["efficacy"]["comparator_failure_induced_reruns"]
    candidate_reruns = sum(generation["readings"]["workflow_retry_counters"].values())
    coverage = len(gauge_results)
    reading = {
        "comparator_failure_induced_reruns": comparator,
        "candidate_failure_induced_reruns": candidate_reruns,
        "failure_induced_rerun_reduction_percent": round(
            ((comparator - candidate_reruns) / comparator) * 100,
            3,
        ),
        "failure_gauges_covered": coverage,
        "failure_gauges_required": contract["efficacy"]["required_failure_gauge_coverage"],
        "caller_supplied_derived_fields": len(contract["caller_supplied_binding_fields"]),
        "new_mutable_current_fixtures": 0,
        "partial_publications": 0,
        "uncaught_escapes": 0,
        "coverage_loss": coverage != comparator,
        "shared_line_growth": line_growth,
        "clean_run_overhead_ms_median": round(clean_run_overhead_ms, 3),
        "timing_acceptance_relevant": False,
    }
    reading["accepted"] = (
        candidate_reruns <= contract["efficacy"]["maximum_candidate_failure_induced_reruns"]
        and coverage == contract["efficacy"]["required_failure_gauge_coverage"]
        and reading["caller_supplied_derived_fields"] == 0
        and reading["new_mutable_current_fixtures"] == 0
        and reading["partial_publications"] == 0
        and reading["uncaught_escapes"] == 0
        and not reading["coverage_loss"]
    )
    return reading


def build_generation(repo_root: Path, contract_path: Path, gauges_path: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    contract = validate_contract(load_json(contract_path))
    latch = validate_latch(
        load_json(repo_root / "orchestration/continuity/ariadne-active-operation-latch/current.json"),
        contract,
    )
    bindings = verify_source_bindings(repo_root, contract)
    gauges = validate_failure_gauges(load_json(gauges_path))
    generation = _derive_generation(repo_root, contract, latch, bindings, gauges)
    validate_generation(generation, contract)
    gauge_results = exercise_failure_gauges(generation, gauges)
    return generation, contract, gauge_results


def measure_clean_run_overhead(
    repo_root: Path,
    contract_path: Path,
    gauges_path: Path,
    *,
    samples: int = 5,
) -> float:
    timings: list[float] = []
    for _ in range(samples):
        start = time.perf_counter_ns()
        build_generation(repo_root, contract_path, gauges_path)
        timings.append((time.perf_counter_ns() - start) / 1_000_000)
    return statistics.median(timings)


def _write_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def authoritative_generation_digest(
    generation: dict[str, Any],
    gauge_results: list[dict[str, str]],
    efficacy: dict[str, Any],
) -> str:
    authoritative_efficacy = {
        key: value
        for key, value in efficacy.items()
        if key != "clean_run_overhead_ms_median"
    }
    return digest(
        {
            "generation": generation,
            "gauge_results": gauge_results,
            "authoritative_efficacy": authoritative_efficacy,
        }
    )


def publish_private_shadow(
    generation: dict[str, Any],
    contract: dict[str, Any],
    gauge_results: list[dict[str, str]],
    efficacy: dict[str, Any],
    target: Path,
    *,
    fail_after_write: int | None = None,
) -> Path:
    validate_generation(generation, contract)
    recalculated = calculate_efficacy(
        contract,
        generation,
        gauge_results,
        line_growth=efficacy["shared_line_growth"],
        clean_run_overhead_ms=efficacy["clean_run_overhead_ms_median"],
    )
    if recalculated != efficacy:
        _reject("publication", "efficacy_integrity")
    if not efficacy.get("accepted"):
        _reject("publication", "efficacy_not_accepted")
    if target.exists():
        _reject("publication", "target_exists")
    if target.name != contract["publication"]["target_leaf"]:
        _reject("publication", "target_leaf")
    lowered = target.as_posix().lower()
    for forbidden in contract["publication"]["forbidden_target_parts"]:
        if f"/{forbidden.lower()}/" in f"/{lowered}/":
            _reject("publication", "forbidden_target")
    staging = target.with_name(f".{target.name}.staging-{uuid.uuid4().hex}")
    files = {
        "journal.json": generation["journal"],
        "work-order.json": generation["work_order"],
        "terminal-result.json": generation["terminal_result"],
        "acknowledgement.json": generation["acknowledgement"],
        "projections.json": generation["projections"],
        "efficacy.json": {**efficacy, "failure_gauge_results": gauge_results},
    }
    try:
        staging.mkdir(parents=False, exist_ok=False)
        written = 0
        file_digests: dict[str, str] = {}
        for name in contract["publication"]["authoritative_files"]:
            if name == "manifest.json":
                continue
            value = files[name]
            _write_json(staging / name, value)
            file_digests[name] = digest(value)
            written += 1
            if fail_after_write == written:
                raise OSError("injected publication failure")
        manifest = {
            "schema_version": "ariadne.shadow_clockwork_private_manifest.v1",
            "acknowledged_tip_sha256": generation["acknowledgement"]["acknowledgement_event_sha256"],
            "authoritative_file_digests": file_digests,
            "generation_sha256": authoritative_generation_digest(
                generation,
                gauge_results,
                efficacy,
            ),
            "timing_excluded_from_authoritative_digest": True,
        }
        _write_json(staging / "manifest.json", manifest)
        for name, expected in file_digests.items():
            if digest(load_json_value(staging / name)) != expected:
                _reject("publication", "staging_readback")
        os.replace(staging, target)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return target


def authoritative_manifest_digest(target: Path) -> str:
    manifest = load_json(target / "manifest.json")
    return manifest["generation_sha256"]
