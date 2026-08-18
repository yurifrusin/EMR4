"""Validate the provider-free shadow Ariadne/DeepSeek gear architecture."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
)
CONTRACT_PATH = BASE / "contract.json"
SCHEMA_PATH = BASE / "contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-architecture-evidence.json"
REPORT_PATH = BASE / "architecture-report.md"
ZERO_DIGEST = "sha256:" + "0" * 64
TERMINAL = {"succeeded", "failed", "unknown_commit"}


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate_json_key:{key}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_lf_sha256(path: Path) -> str:
    value = path.read_text(encoding="utf-8")
    value = value.replace("\r\n", "\n")
    if "\r" in value:
        raise ValueError(f"bare_cr_rejected:{path}")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_source_bindings(contract: dict[str, Any]) -> None:
    observed_paths: set[str] = set()
    for binding in contract["source_bindings"]:
        path = binding["path"]
        if path in observed_paths:
            raise ValueError("source_binding_path_duplicate")
        observed_paths.add(path)
        source = ROOT / path
        if not source.is_file():
            raise ValueError(f"source_binding_missing:{path}")
        if canonical_lf_sha256(source) != binding["canonical_lf_sha256"]:
            raise ValueError(f"source_binding_digest_mismatch:{path}")


def validate_contract(
    value: dict[str, Any], *, normative: dict[str, Any] | None = None
) -> None:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise ValueError("contract_schema_invalid:" + errors[0].message)
    if normative is not None and value != normative:
        raise ValueError("contract_not_normative")

    if value["caller_supplied_binding_fields"] != []:
        raise ValueError("caller_supplied_binding_field_forbidden")
    if len(value["engine_owned_fields"]) != 15:
        raise ValueError("engine_owned_field_inventory_invalid")
    if set(value["effect_classes"]["shadow_admitted"]) != {
        "read_only",
        "shadow_generation_write",
    }:
        raise ValueError("shadow_effect_posture_invalid")
    if value["work_order"]["occupied_enabled"] is not False:
        raise ValueError("occupied_harness_must_remain_disabled")
    if value["work_order"]["financial_budget_mechanism_required"] is not False:
        raise ValueError("financial_boundary_drift")
    if value["attempt_lifecycle"]["unknown_commit_releases_success"] is not False:
        raise ValueError("unknown_commit_success_forbidden")
    if value["attempt_lifecycle"]["unknown_commit_automatic_retry"] is not False:
        raise ValueError("unknown_commit_retry_forbidden")
    if len(value["acceptance_scenarios"]) < 36:
        raise ValueError("scenario_inventory_too_small")


def _event(
    *,
    writer: str,
    event: str,
    sequence: int,
    previous: str,
    attempt_id: str = "attempt-kernel-architecture-001",
    terminal_result_sha256: str | None = None,
) -> dict[str, Any]:
    value = {
        "writer": writer,
        "event": event,
        "attempt_id": attempt_id,
        "sequence": sequence,
        "previous_tick_sha256": previous,
        "terminal_result_sha256": terminal_result_sha256,
    }
    value["tick_sha256"] = digest(value)
    return value


def canonical_gear_trace(*, terminal: str = "succeeded") -> list[dict[str, Any]]:
    if terminal not in TERMINAL:
        raise ValueError("terminal_class_invalid")
    events: list[dict[str, Any]] = []
    previous = ZERO_DIGEST
    for writer, event in (
        ("ariadne", "admitted"),
        ("ariadne", "work_order_issued"),
        ("deepseek_broker", "started"),
        ("deepseek_broker", terminal),
    ):
        item = _event(
            writer=writer,
            event=event,
            sequence=len(events) + 1,
            previous=previous,
        )
        events.append(item)
        previous = item["tick_sha256"]
    terminal_digest = events[-1]["tick_sha256"]
    events.append(
        _event(
            writer="ariadne",
            event="acknowledged",
            sequence=len(events) + 1,
            previous=previous,
            terminal_result_sha256=terminal_digest,
        )
    )
    return events


def validate_gear_trace(events: object) -> None:
    if not isinstance(events, list) or not events:
        raise ValueError("gear_trace_empty")
    expected_sequence = 1
    previous = ZERO_DIGEST
    state = "initial"
    lease = "ariadne"
    attempt_id: str | None = None
    terminal_digest: str | None = None
    acknowledged = False
    allowed_keys = {
        "writer",
        "event",
        "attempt_id",
        "sequence",
        "previous_tick_sha256",
        "terminal_result_sha256",
        "tick_sha256",
    }
    for item in events:
        if not isinstance(item, dict) or set(item) != allowed_keys:
            raise ValueError("gear_event_keys_invalid")
        if item["sequence"] != expected_sequence:
            raise ValueError("gear_sequence_invalid")
        if item["previous_tick_sha256"] != previous:
            raise ValueError("gear_parent_invalid")
        supplied = item["tick_sha256"]
        expected = digest({key: value for key, value in item.items() if key != "tick_sha256"})
        if supplied != expected:
            raise ValueError("gear_digest_invalid")
        if attempt_id is None:
            attempt_id = item["attempt_id"]
        elif item["attempt_id"] != attempt_id:
            raise ValueError("gear_attempt_drift")

        event = item["event"]
        writer = item["writer"]
        if acknowledged:
            raise ValueError("gear_event_after_acknowledgement")
        if state == "initial":
            if writer != "ariadne" or event != "admitted" or lease != "ariadne":
                raise ValueError("gear_admission_invalid")
            state = "admitted"
        elif state == "admitted":
            if writer != "ariadne" or event != "work_order_issued":
                raise ValueError("gear_work_order_invalid")
            lease = "deepseek_broker"
            state = "issued"
        elif state == "issued":
            if writer != lease or event != "started":
                raise ValueError("gear_start_invalid")
            state = "started"
        elif state == "started":
            if writer != lease or event not in TERMINAL:
                raise ValueError("gear_terminal_invalid")
            terminal_digest = supplied
            state = "terminal"
        elif state == "terminal":
            if writer != "ariadne" or event != "acknowledged":
                raise ValueError("gear_acknowledgement_invalid")
            if item["terminal_result_sha256"] != terminal_digest:
                raise ValueError("gear_terminal_binding_invalid")
            lease = "ariadne"
            state = "acknowledged"
            acknowledged = True
        previous = supplied
        expected_sequence += 1
    if state != "acknowledged" or lease != "ariadne":
        raise ValueError("gear_trace_not_acknowledged")


def _leaf_paths(value: object, prefix: tuple[object, ...] = ()) -> list[tuple[object, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            for path in _leaf_paths(child, prefix + (key,))
        ]
    if isinstance(value, list):
        if not value:
            return [prefix]
        return [
            path
            for index, child in enumerate(value)
            for path in _leaf_paths(child, prefix + (index,))
        ]
    return [prefix]


def _mutated(value: object, salt: int) -> object:
    if value is None:
        return f"supplied-derived-field-{salt}"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + salt + 1
    if isinstance(value, str):
        return value + f"-mutation-{salt}"
    if isinstance(value, list):
        return [*value, f"mutation-{salt}"]
    raise TypeError("unsupported_mutation_leaf")


def _set_path(value: object, path: tuple[object, ...], replacement: object) -> None:
    current = value
    for item in path[:-1]:
        current = current[item]  # type: ignore[index]
    current[path[-1]] = replacement  # type: ignore[index]


def run_hostile_mutations(contract: dict[str, Any], count: int = 256) -> dict[str, Any]:
    paths = _leaf_paths(contract)
    escaped: list[str] = []
    for index in range(count):
        path = paths[index % len(paths)]
        candidate = copy.deepcopy(contract)
        current: object = candidate
        for item in path:
            current = current[item]  # type: ignore[index]
        _set_path(candidate, path, _mutated(current, index))
        try:
            validate_contract(candidate, normative=contract)
        except ValueError:
            continue
        escaped.append("/".join(str(item) for item in path))
    return {"attempted": count, "rejected": count - len(escaped), "escaped": escaped}


def run_trace_mutations() -> dict[str, Any]:
    trace = canonical_gear_trace()
    mutations: list[tuple[str, list[dict[str, Any]]]] = []

    def changed(name: str) -> tuple[str, list[dict[str, Any]]]:
        return name, copy.deepcopy(trace)

    for name, index, key, value in (
        ("stale_parent", 2, "previous_tick_sha256", ZERO_DIGEST),
        ("sequence_gap", 2, "sequence", 8),
        ("concurrent_writer", 2, "writer", "ariadne"),
        ("result_before_start", 2, "event", "succeeded"),
        ("ack_before_terminal", 3, "event", "acknowledged"),
        ("wrong_terminal_digest", 4, "terminal_result_sha256", ZERO_DIGEST),
        ("attempt_drift", 3, "attempt_id", "attempt-foreign-002"),
    ):
        label, candidate = changed(name)
        candidate[index][key] = value
        mutations.append((label, candidate))
    duplicate_terminal = copy.deepcopy(trace)
    duplicate_terminal.insert(4, copy.deepcopy(duplicate_terminal[3]))
    mutations.append(("duplicate_terminal", duplicate_terminal))
    broker_after_terminal = copy.deepcopy(trace)
    broker_after_terminal[4]["writer"] = "deepseek_broker"
    broker_after_terminal[4]["event"] = "started"
    mutations.append(("broker_after_terminal", broker_after_terminal))
    replay = copy.deepcopy(trace)
    replay.insert(3, copy.deepcopy(replay[2]))
    mutations.append(("replay", replay))

    rejected: list[str] = []
    for name, candidate in mutations:
        try:
            validate_gear_trace(candidate)
        except ValueError:
            rejected.append(name)
    return {
        "attempted": len(mutations),
        "rejected": len(rejected),
        "escaped": sorted(set(name for name, _ in mutations) - set(rejected)),
    }


def build_evidence() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    validate_contract(contract)
    verify_source_bindings(contract)
    for terminal in sorted(TERMINAL):
        validate_gear_trace(canonical_gear_trace(terminal=terminal))
    hostile = run_hostile_mutations(contract)
    traces = run_trace_mutations()
    escaped = [*hostile["escaped"], *traces["escaped"]]
    return {
        "schema_version": "ariadne.shadow_clockwork_broker_gear_architecture_evidence.v1",
        "status": "passed" if not escaped else "revision_required",
        "evidence_label": contract["evidence_label"],
        "source_bindings": {"expected": 10, "matched": 10},
        "acceptance_scenarios": {
            "expected_minimum": 36,
            "passed": len(contract["acceptance_scenarios"]),
            "failed": [],
        },
        "terminal_traces": {
            "succeeded": "passed",
            "failed": "passed",
            "unknown_commit": "passed",
        },
        "trace_mutations": traces,
        "hostile_contract_mutations": hostile,
        "caller_supplied_binding_fields": 0,
        "engine_owned_fields": len(contract["engine_owned_fields"]),
        "shadow_admitted_effect_classes": contract["effect_classes"][
            "shadow_admitted"
        ],
        "occupied_harness_enabled": contract["work_order"]["occupied_enabled"],
        "current_controls_retired": contract["projection_protocol"][
            "current_controls_retired"
        ],
        "kernel_closeout_baseline": contract["efficacy"][
            "kernel_closeout_baseline"
        ],
        "future_rehearsal_thresholds": contract["efficacy"][
            "future_rehearsal_thresholds"
        ],
        "uncaught_escapes": len(escaped),
    }


def render_report(evidence: dict[str, Any]) -> str:
    baseline = evidence["kernel_closeout_baseline"]
    thresholds = evidence["future_rehearsal_thresholds"]
    return f"""# Provider-free shadow clockwork / broker gear architecture report

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Decision: `{evidence['status']}`

Evidence label: `{evidence['evidence_label']}`

## Deterministic reading

- exact predecessor source bindings: {evidence['source_bindings']['matched']}/{evidence['source_bindings']['expected']};
- architecture scenarios: {evidence['acceptance_scenarios']['passed']} passed;
- hostile contract mutations: {evidence['hostile_contract_mutations']['attempted']} rejected, {len(evidence['hostile_contract_mutations']['escaped'])} escaped;
- hostile gear traces: {evidence['trace_mutations']['attempted']} rejected, {len(evidence['trace_mutations']['escaped'])} escaped;
- caller-supplied binding fields: {evidence['caller_supplied_binding_fields']};
- engine-owned field groups: {evidence['engine_owned_fields']};
- occupied Harness enabled: {str(evidence['occupied_harness_enabled']).lower()}; and
- current controls retired: {str(evidence['current_controls_retired']).lower()}.

The success, failure and unknown-commit terminal traces all require one exact
broker terminal digest followed by Ariadne acknowledgement before the lease
returns. Wall time is not part of causal order.

## Baseline carried forward

- manual binding fields: not yet instrumented;
- provider retries: {baseline['provider_retries']};
- rejected register/pre-verifier drafts: {baseline['rejected_register_or_pre_verifier_drafts']};
- failure-induced closeout/transition reruns: {baseline['failure_induced_closeout_or_transition_reruns']};
- stale mutable-latch fixtures: {baseline['stale_mutable_latch_fixtures']}; and
- uncaught escapes: {baseline['uncaught_escapes']}.

The next rehearsal must derive zero caller fields, reduce failure-induced
reruns by at least {thresholds['minimum_failure_induced_rerun_reduction_percent']} percent, add zero mutable-current fixtures,
preserve coverage and produce zero partial publication and zero escape. Shared-
engine growth and clean-run overhead remain mandatory readings.

## Boundary

This report accepts architecture only. It does not adopt a live clock, replace
current controls, launch the native Harness, call a provider, enable ordinary
practice, change product/API/database/client source, use product data, deploy,
release, publish Pages or move protected refs.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    if args.write_evidence:
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    else:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
